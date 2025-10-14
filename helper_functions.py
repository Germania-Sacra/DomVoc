import re
import pandas as pd
import numpy as np
import os
from SPARQLWrapper import SPARQLWrapper, JSON

# Code from https://github.com/WIAG-ADW-GOE/sync_notebooks/blob/main/wiag_to_factgrid.ipynb, last updated 2025-07-01 11:58

#defining an enum to more clearly define what type of date is being passed 
from enum import Enum
import re
from datetime import datetime

class DateType(Enum):
    ONLY_DATE = 0
    BEGIN_DATE = 1
    END_DATE = 2

#date precision (https://www.wikidata.org/wiki/Help:QuickStatements)
PRECISION_CENTURY = 7
PRECISION_DECADE = 8
PRECISION_YEAR = 9

#defining some constants for better readability of the code:
#self defined:
JULIAN_ENDING = '/J'
JHS_GROUP = r'(Jhs\.|Jahrhunderts?)'
JH_GROUP = r'(Jh\.|Jahrhundert)'
EIGTH_OF_A_CENTURY = 13
QUARTER_OF_A_CENTURY = 25
TENTH_OF_A_CENTURY = 10

ANTE_GROUP = "bis|vor|spätestens"
POST_GROUP = "nach|frühestens|ab"
CIRCA_GROUP = r"etwa|ca\.|um"
#pre-compiling the most complex pattern to increase efficiency
MOST_COMPLEX_PATTERN = re.compile(r'(wohl )?((kurz )?(' + ANTE_GROUP + '|' + POST_GROUP + r') )?((' + CIRCA_GROUP +r') )?(\d{3,4})(\?)?')

#FactGrid properties:
    # simple date properties:
DATE = 'P106' 
BEGIN_DATE = 'P49'
END_DATE = 'P50'
    # when there is uncertainty / when all we know is the latest/earliest possible date:
DATE_AFTER = 'P41' # the earliest possible date for something
DATE_BEFORE = 'P43' # the latest possible date for something
END_TERMINUS_ANTE_QUEM = 'P1123' # latest possible date of the end of a period
BEGIN_TERMINUS_ANTE_QUEM  = 'P1124' # latest possible date of the begin of a period
END_TERMINUS_POST_QUEM = 'P1125' # earliest possible date of the end of a period
BEGIN_TERMINUS_POST_QUEM = 'P1126' # earliest possible date of the beginning of a period

NOTE = 'P73' # Field for free notes
PRECISION_DATE = 'P467' # FactGrid qualifier for the specific determination of the exactness of a date
PRECISION_BEGIN_DATE = 'P785'   # qualifier to specify a begin date
PRECISION_END_DATE = 'P786'
STRING_PRECISION_BEGIN_DATE = 'P787' # qualifier to specify a begin date; string alternate to P785
STRING_PRECISION_END_DATE = 'P788'

#qualifiers/options
SHORTLY_BEFORE = 'Q255211'
SHORTLY_AFTER = 'Q266009'
LIKELY = 'Q23356'
CIRCA = 'Q10'
OR_FOLLOWING_YEAR = 'Q912616'

def construct_description(location_name, monastery_name, location_begin_taq, location_begin_tpq, location_end_taq, location_end_tpq):
    ret_str = f"Gebäudekomplex{" "+location_name if not pd.isna(location_name) else ""} des {monastery_name}"
    # if not pd.isna(location_begin_taq):
    #     if not pd.isna(location_begin_tpq):
    #         ret_str += f" ab etwa {int(location_begin_tpq)}/{int(location_begin_taq)}"
    #     else:
    #         ret_str += f" ab etwa {int(location_begin_taq)}"
    # elif not pd.isna(location_begin_tpq):
    #     ret_str += f" ab etwa {int(location_begin_tpq)}"

    # if not pd.isna(location_end_taq):
    #     if not pd.isna(location_end_tpq):
    #         ret_str += f" bis etwa {int(location_end_tpq)}/{int(location_end_taq)}"
    #     else:
    #         ret_str += f" bis etwa {int(location_end_taq)}"
    # elif not pd.isna(location_end_tpq):
    #     ret_str += f" bis etwa {int(location_end_tpq)}"

    # Fix Grammar
    m = re.search('des .*(kloster|stift|kolleg|priorat)', ret_str)
    if(m): 
        ret_str = ret_str.replace(m.group(), m.group()+'s')
        return ret_str

    m = re.search('des .*haus', ret_str)
    if(m): 
        ret_str = ret_str.replace(m.group(), m.group()+'es')
        return ret_str

    m = re.search('des( .*(kommende|komturei|herren|niederlassung|propstei|abtei|sammlung))', ret_str)
    if(m):
        ret_str = ret_str.replace(m.group(), "der" + m.group(1))
        return ret_str
    
    m = re.search('des Unbeschuhte', ret_str)
    if(m):
        ret_str = ret_str.replace(m.group(), "der Unbeschuhten")
        return ret_str


    return ret_str

def df_to_qs_v1(df:pd.DataFrame):
    # Preparation: rename identical columns (won't change column names in end result, but necessary to keep all Source Columns)
    cols=pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique(): 
        cols[cols[cols == dup].index.values.tolist()] = [dup + '.' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns=cols
    # Transform Datframe to Dictionary
    df_dict = df.to_dict(orient="records")
    output_collect = ""
    # For every "row" in the table (now entry in dictionary)...
    for item in df_dict:
        output = ""
        create_flag = False
        keys = list(item.keys())
        i = 0
        qid = None
        # ... iterate over all columns names in this row, and ...
        while i < len(keys):
            out_str = ""
            # ... look at every column name:
            k = keys[i]
            # If it is a source statement (starts with S, followed by a numerical character, e.g. S471), or a qualifier:
            # Skip for now, it will be dealt with later
            if (k.startswith("S") and not k[1].isalpha()) or k.startswith("qal"):
                i += 1
                continue
            # If it is the "qid" column:
            if k == "qid":
                # If it is empty, set flag for new item creation and add CREATE keyword ...
                if pd.isna(item["qid"]):
                    create_flag = True
                    out_str += "CREATE\n"
                # ... otherwise, begin line with qid
                else:
                    qid = item["qid"]
            # In all other cases: If there is a value in this column...
            elif not pd.isna(item[k]):
                #... start line with keyword LAST if a new item is being created ...
                if create_flag:
                    out_str += "LAST"
                # ... or with the qid of the item that should be changed
                else:
                    out_str += qid
                # ... then add information from the column to the line
                out_str += f"\t{k}\t{item[k]}"
                # As long as the following columns are Source-Statements or qualifiers, ...
                while i+1 < len(keys) and ((keys[i+1].startswith("S") and not keys[i+1][1].isalpha()) or keys[i+1].startswith("qal")):
                    k = keys[i+1]
                    # ... add the column names and values to the current line, if they contain a value
                    if k.startswith("qal"):
                        k_rep = k.replace("qal", "P")
                        if(not pd.isna(item[k])):
                            out_str += f'\t{k_rep.split(".")[0]}\t{item[k]}'
                        i += 1
                    else:
                        if(not pd.isna(item[k])):
                            out_str += f'\t{k.split(".")[0]}\t{item[k]}'
                        i += 1
                # End current line with newline Character
                out_str += "\n"
            # and append to file
            output += out_str
            i += 1
        output_collect += output
    return output_collect
                
def load_files_from_folder(filepath, file_extension):
    export_files = {}
    for export_file in os.listdir(filepath):
        if export_file.endswith(file_extension):
            export_files[export_file.split(".")[0]] = f"{filepath}/{export_file}"
    return export_files

def format_datetime(entry: datetime, precision: int):
    ret_val =  f"+{entry.isoformat()}Z/{precision}"

    if entry.year < 1582:
        ret_val +=  JULIAN_ENDING
    
    if precision <= 9:
        ret_val = ret_val.replace(f"{entry.year}-01-01", f"{entry.year}-00-00", 1)

    return ret_val

#only_date=True means there is only one date, not a 'begin date' and an 'end date'
def date_parsing(date_string: str, date_type: DateType):
    qualifier = ""
    entry = None
    precision = PRECISION_CENTURY

    ante_property = (match := re.search(ANTE_GROUP, date_string))
    post_property = (match := re.search(POST_GROUP, date_string))
    assert(not ante_property or not post_property)
    
    match date_type:
        case DateType.ONLY_DATE:
            string_precision_qualifier_clause = NOTE
            exact_precision_qualifier = PRECISION_DATE
            if ante_property:
                return_property = DATE_BEFORE
            elif post_property:
                return_property = DATE_AFTER
            else:
                return_property = DATE
        case DateType.BEGIN_DATE:
            string_precision_qualifier_clause = STRING_PRECISION_BEGIN_DATE
            exact_precision_qualifier = PRECISION_BEGIN_DATE
            if ante_property:
                return_property = BEGIN_TERMINUS_ANTE_QUEM
            elif post_property:
                return_property = BEGIN_TERMINUS_POST_QUEM
            else:
                return_property = BEGIN_DATE
        case DateType.END_DATE:
            string_precision_qualifier_clause = STRING_PRECISION_END_DATE
            exact_precision_qualifier = PRECISION_END_DATE
            if ante_property:
                return_property = END_TERMINUS_ANTE_QUEM
            elif post_property:
                return_property = END_TERMINUS_POST_QUEM
            else:
                return_property = END_DATE    
        case _:
            assert False, "Unexpected DateType!"
        
    string_precision_qualifier_clause += f'\t"{date_string}"'

    if date_string == '?':
        return tuple()
            
    if matches := re.match(r'(\d{1,2})\. ' + JH_GROUP, date_string):
        centuries = int(matches.group(1))
        entry = datetime(100 * (centuries), 1, 1)
    
    elif matches := re.match(r'(\d)\. Hälfte (des )?(\d{1,2})\. ' + JHS_GROUP, date_string):
        half = int(matches.group(1)) - 1
        centuries = int(matches.group(3)) - 1
        year   = centuries * 100 + (half * 50) + QUARTER_OF_A_CENTURY
        entry = datetime(year, 1, 1)
        qualifier = string_precision_qualifier_clause
    
    elif matches := re.match(r'(\w+) Viertel des (\d{1,2})\. ' + JHS_GROUP, date_string):
        number_map = {
            "erstes":  0,
            "zweites": 1,
            "drittes": 2,
            "viertes": 3,
        }
        quarter = matches.group(1)
        centuries = int(matches.group(2))
        year = (centuries - 1) * 100 + (number_map[quarter] * 25) + EIGTH_OF_A_CENTURY
        entry = datetime(year, 1, 1)
        qualifier = string_precision_qualifier_clause

    elif matches := re.match(r'frühes (\d{1,2})\. ' + JH_GROUP, date_string):
        centuries = int(matches.group(1)) - 1
        year = centuries * 100 + TENTH_OF_A_CENTURY
        entry = datetime(year, 1, 1)
        qualifier = string_precision_qualifier_clause

    elif matches := re.match(r'spätes (\d{1,2})\. ' + JH_GROUP, date_string):
        centuries = int(matches.group(1))
        year = centuries * 100 - TENTH_OF_A_CENTURY
        entry = datetime(year, 1, 1)
        qualifier = string_precision_qualifier_clause

    elif matches := re.match(r'(Anfang|Mitte|Ende) (\d{1,2})\. ' + JH_GROUP, date_string):
        number_map = {
            "Anfang":  0,
            "Mitte": 1,
            "Ende": 2,
        }
        third = number_map[matches.group(1)]
        centuries = int(matches.group(2)) - 1
        year = centuries * 100 + (third * 33) + 17
        entry = datetime(year, 1, 1)
        qualifier = string_precision_qualifier_clause

    elif matches := re.match(r'(\d{3,4})er Jahre', date_string):
        entry = datetime(int(matches.group(1)), 1, 1)
        precision = PRECISION_DECADE
    
    elif matches := re.match(r'Wende zum (\d{1,2})\. ' + JH_GROUP, date_string):
        centuries = int(matches.group(1)) - 1
        entry = datetime(centuries * 100 - 10, 1, 1)
        qualifier = string_precision_qualifier_clause

    elif matches := re.match(r'Anfang der (\d{3,4})er Jahre', date_string):
        entry = datetime(int(matches.group(1)), 1, 1)
        qualifier = string_precision_qualifier_clause
        precision = PRECISION_DECADE

    elif matches := re.match(r'\((\d{3,4})\s?\?\) (\d{3,4})', date_string):
        entry = datetime(int(matches.group(2)), 1, 1) # ignoring the year in parantheses
        precision = PRECISION_YEAR
        qualifier = string_precision_qualifier_clause
    
    elif matches := re.match(r'(\d{3,4})/(\d{3,4})', date_string):
        year1 = int(matches.group(1))
        year2 = int(matches.group(2))

        if year2 - year1 == 1:
            # check for consecutive years
            qualifier = exact_precision_qualifier + '\t' + OR_FOLLOWING_YEAR
        entry = datetime(year1, 1, 1)
        precision = PRECISION_YEAR

    # this pattern is pre-compiled above, because it's rather complex and it's much more efficient to compile it just once, instead of on every function call
    elif matches := MOST_COMPLEX_PATTERN.match(date_string):
        if matches.group(1): # if 'wohl' was found
            qualifier = exact_precision_qualifier + '\t' + LIKELY
        if matches.group(5): # if 'etwa' , 'ca.' or 'um' were found
            if len(qualifier) != 0:
                qualifier += '\t'
            qualifier += exact_precision_qualifier + '\t' + CIRCA
                
        if matches.group(3): # if 'kurz' was found -- because of how the regex is defined, this can only happen when combined with 'nach', 'bis', etc.
            if len(qualifier) != 0:
                qualifier += '\t'

            if ante_property: # already checked above whether it's before or after
                qualifier += exact_precision_qualifier + '\t' + SHORTLY_BEFORE
            else: # post_property
                qualifier += exact_precision_qualifier + '\t' + SHORTLY_AFTER

        if matches.group(8): # if a question mark at the end were found
            # TODO is it correct, that on ? the other matches ('ca.' etc.) are ignored, because it's not exact enough?
            qualifier = string_precision_qualifier_clause
        
        entry = datetime(int(matches.group(7)), 1, 1)
        precision = PRECISION_YEAR

    else:
        raise Exception(f"Couldn't parse date '{date_string}'")
        
    return (return_property, format_datetime(entry, precision), qualifier)

def parse_date(date, date_type):
    try:
        result = date_parsing(date, date_type)
    except:
        return np.nan
    return result

def format_date(d, precision):
    if pd.isnull(d):
        return np.nan
    if int(d) < 1582:
        return f'+{int(d)}-01-01T00:00:00Z/{precision}/J'
    else:
        return f'+{int(d)}-01-01T00:00:00Z/{precision}'

def process_individual_parsing_result(df, index, row, result_column, mode):
    if result_column == "begin_date_parse_result" and pd.isnull(row[f'{mode}_begin_note']):
        if not pd.isnull(row[f'{mode}_begin_tpq']):
            df.loc[index, "qal49"] = format_date(row[f'{mode}_begin_tpq'], 9)
    if result_column == "end_date_parse_result" and pd.isnull(row[f'{mode}_end_note']):
        if not pd.isnull(row[f'{mode}_end_tpq']):
            df.loc[index, "qal50"] = format_date(row[f'{mode}_end_tpq'], 9)
    if not pd.isnull(row[result_column]):
        try:
            p, date_str, qal = row[result_column]
            df.loc[index, p.replace("P", "qal")] = date_str
            i = 0
            while i+1 < len(qal.split("\t")):
                df.loc[index, qal.split("\t")[i].replace("P", "qal")] = qal.split("\t")[i+1]
                i += 2
        except:
            print(row[result_column])
    if result_column == "begin_date_parse_result" and not pd.isnull(row[f'{mode}_begin_note']) and pd.isnull(row[result_column]) and "Jahrhundert" in row[f'{mode}_begin_note']:
        df.loc[index, "qal49"] = format_date(row[f'{mode}_begin_tpq'], 7)
    elif result_column == "begin_date_parse_result" and not pd.isnull(row[f'{mode}_begin_note']) and pd.isnull(row[result_column]):
        df.loc[index, "qal49"] = format_date(row[f'{mode}_begin_tpq'], 9)
    if result_column == "end_date_parse_result" and not pd.isnull(row[f'{mode}_end_note']) and pd.isnull(row[result_column]) and "Jahrhundert" in row[f'{mode}_end_note']:
        df.loc[index, "qal50"] = format_date(row[f'{mode}_end_tpq'], 7)
    elif result_column == "end_date_parse_result" and not pd.isnull(row[f'{mode}_end_note']) and pd.isnull(row[result_column]):
        df.loc[index, "qal50"] = format_date(row[f'{mode}_end_tpq'], 9)

def process_date_parsing_results(df, mode):
    for index, row in df.iterrows():
        process_individual_parsing_result(df, index, row, "begin_date_parse_result", mode)
        process_individual_parsing_result(df, index, row, "end_date_parse_result", mode)


def query_factgrid(queryname):
    ENDPOINT = "https://database.factgrid.de/sparql"

    monastery_query = """
    SELECT ?item ?KlosterdatenbankID WHERE{
        ?item wdt:P471 ?KlosterdatenbankID 
    }
    """

    building_complex_query = """
    SELECT ?item ?GSVocabTerm WHERE{
    ?item wdt:P2 wd:Q635758 .
    ?item wdt:P1301 ?GSVocabTerm
        }
    """

    query_mapping = {"monasteries":monastery_query, "building_complexes":building_complex_query}

    sparql = SPARQLWrapper(ENDPOINT)
    sparql.setQuery(query_mapping[queryname])
    sparql.setReturnFormat(JSON)

    results = sparql.query().convert()

    # Flatten the JSON → list of dicts → DataFrame
    rows = [
        {key: val["value"] for key, val in binding.items()}
        for binding in results["results"]["bindings"]
    ]
    df = pd.DataFrame(rows)
    return df