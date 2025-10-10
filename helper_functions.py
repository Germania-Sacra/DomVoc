import re
import pandas as pd
import numpy as np

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
    cols=pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique(): 
        cols[cols[cols == dup].index.values.tolist()] = [dup + '.' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    df.columns=cols
    df_dict = df.to_dict(orient="records")
    output_collect = ""
    for item in df_dict:
        output = ""
        create_flag = False
        keys = list(item.keys())
        i = 0
        qid = None
        while i < len(keys):
            out_str = ""
            k = keys[i]
            if k.startswith("S") or k.startswith("qal"):
                i += 1
                continue
            if k == "qid":
                if pd.isna(item["qid"]):
                    create_flag = True
                    out_str += "CREATE\n"
                else:
                    qid = item["qid"]
            elif not pd.isna(item[k]):
                if create_flag:
                    out_str += "LAST"
                else:
                    out_str += qid
                out_str += f"\t{k}\t{item[k]}"
                while i+1 < len(keys) and (keys[i+1].startswith("S") or keys[i+1].startswith("qal")):
                    k = keys[i+1]
                    if k.startswith("qal"):
                        k_rep = k.replace("qal", "P")
                        if(not pd.isna(item[k])):
                            out_str += f'\t{k_rep.split(".")[0]}\t{item[k]}'
                        i += 1
                    else:
                        if(not pd.isna(item[k])):
                            out_str += f'\t{k.split(".")[0]}\t{item[k]}'
                        i += 1
                out_str += "\n"
            output += out_str
            i += 1
        output_collect += output
    return output_collect
                
                

