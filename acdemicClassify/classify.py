import pandas as pd
import re
import Levenshtein


def is_Chinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False


def read_reference(file):
    dictpaper = {}
    with open("reference.txt", "r") as file1:
        rows = file1.readlines()
        for item in rows:
            shortName, name, grade, paperType = item.replace("\n","").split("\t")[1:5]
            name = name.lower()
            shortName = shortName.lower()
            if name not in dictpaper.keys():
                dictpaper[name] = (grade, paperType)
            if shortName not in dictpaper.keys():
                dictpaper[shortName] = (grade, paperType)
    return dictpaper


# def fuzzy_finder(user_input, collection):
#     suggestions = []
#     print(user_input)
#     pattern = '.*?'.join(user_input)  # Converts 'djm' to 'd.*?j.*?m'
#     regex = re.compile(pattern)  # Compiles a regex.
#     for item in collection:
#         match = regex.search(item)  # Checks if the current item matches the regex.
#         if match:
#             suggestions.append((len(match.group()), match.start(), item))
#     return [x for _, _, x in sorted(suggestions)]

def similar(user_input, collection):
    similarlist = []
    for item in collection:
        user_input1 = user_input.replace(" ","")
        item1 = item.replace(" ","")
        probility = (len(user_input1)-Levenshtein.distance(user_input1, item1))/len(user_input1)
        similarlist.append((item,probility))
    result = sorted(similarlist, key=lambda a: a[1],reverse=True)
    return result[:1]


def classify():
    file1 = pd.read_excel("paper2018.xlsx", sheet_name='2018')
    conference = file1[file1['类型'].str.contains("会议")]
    journal = file1[file1['类型'].str.contains("期刊")]
    # 会议数量
    numconf = len(conference)
    # 期刊数量
    numjour = len(journal)
    # print(journal)
    # 总数应该等于列表行数，不等则类型列不完整
    conflist = conference.values.tolist()
    jourlist = journal.values.tolist()
    # for item in jourlist:
    #     print(item)
    # CCF会议名称与简称等级字典
    dictpaper = read_reference("reference.txt")
    namelist = dictpaper.keys()
    result1 = matchresult(conflist,namelist,dictpaper)
    result2 = matchresult(jourlist,namelist,dictpaper)
    df = pd.DataFrame(result1+result2, columns=['论文名称', '作者', '发表期刊(会议)名称', '类型', '年份', '匹配结果', '级别', '类型', '预测'])
    df.to_csv("result2018.csv", encoding="utf_8_sig")


def matchresult(conflist,namelist,dictpaper):
    classifyres = []
    count = 0
    for data in conflist:
        # 中文期刊会议跳过
        # print(data[2])
        if is_Chinese(data[2]):
            continue
        for i in range(10):
            temp = data[2].lower().replace(str(i), "")
        # 完全匹配会议简称与全名
        if temp in namelist:
            grade, typepaper = dictpaper[temp]
            if (grade == "A类" or grade == "B类") and typepaper in data[3]:
                res = data+[temp, grade, typepaper, 1]
                classifyres.append(res)
                count +=1
        else:
            suggestlist = similar(temp, dictpaper.keys())
            if suggestlist == []:
                print("查无相近名称")
            # 计算模糊推荐名称与搜索名称相似度，概率小越好
            for item in suggestlist:
                name, probility = item
                grade, typepaper = dictpaper[name]
                if (grade == "A类" or grade == "B类") and typepaper in data[3]:
                    res = data + [name, grade, typepaper, probility]
                    classifyres.append(res)
                    count += 1
    print(count)
    # print(len(classifyres))
    result = sorted(classifyres, key=lambda l: (l[-3],l[-1]),reverse=True)
    return result



if __name__ == "__main__":
    classify()
    # dictpaper = read_reference("reference.txt")
    # print(fuzzy_finder("AA",dictpaper.keys()))

# for i in range(numconf):
#     print(conference.loc[:,i])
# print(conference.loc[0,:])
# print(journal)

# for data in file1['类型']:
#     print(data)
#     if("期刊" in data):
#         journal.append(data)
#     elif ("会议" in data):
#         conference.append(data)
#     else:
#         other.append(data)
# print(journal)
# print("#####")
# print(other)




