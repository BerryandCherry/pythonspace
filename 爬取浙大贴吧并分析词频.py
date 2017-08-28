import requests, sys, webbrowser,bs4
from bs4 import BeautifulSoup
def GetURL(URL,list_b):
    res=requests.get(URL)
    print(URL)
    res.raise_for_status()
    print(res)
    soup=bs4.BeautifulSoup(res.content,'lxml')
    with open('170820.txt', 'w',encoding='utf8') as g:
        g.write(soup.prettify())
    #获取所有链接
    list_a = [tag.get('href') for tag in soup.select('a[href]')] 
    for a in range(len(list_a)):
        if '/p/' in list_a[a][0:3]:
            list_b.append(list_a[a])
    return soup


def GetPage(soup):
    #获取页数信息
    list_c=soup.find_all("a","pagination-item")
    list_d=list_c
    i=0
    for link in soup.find_all("a","pagination-item"):
        list_d[i],i='http:'+link.get('href'),i+1
    return list_d



def GetInfo(soup):#获取二级页面的所有贴子
    list_f=[]
    f = soup.find_all('a',  attrs={'class': 'j_th_tit'})
    #获取所有的帖子的代码
    #根据属性获取，也可以写成('a','j_th_tit')
    list_f=[tag.get('title') for tag in f]#获取帖子标题
    return list_f


with open('目录标题.txt', 'w',encoding='utf8') as g:
    list_b=[]#
    mySoup=GetURL('http://tieba.baidu.com/f?kw=%E6%B5%99%E6%B1%9F%E5%A4%A7%E5%AD%A6&fr=wwwt',list_b)
    list_c=GetPage(mySoup)
    print(list_c)
    print(list_b)
    list_f=GetInfo(mySoup)
    for i in list_f:
        g.write(i+'\n')

#要进入查看每一个贴子。(list_b)并构造soup对象
count=0
first_current_url='http://tieba.baidu.com/f?kw=%E6%B5%99%E6%B1%9F%E5%A4%A7%E5%AD%A6&ie=utf-8&&pn=0'
first_pagenum=1
first_maxnum=5
with open('tieba.txt','w',encoding='utf8') as g:
    while first_pagenum<=first_maxnum:
        first_prefix='first_'+str(first_pagenum)
        first_pagenum=first_pagenum+1
        list_b=[]
        first_soup=GetURL(first_current_url,list_b)
        topic_list=GetInfo(first_soup)
        #print(list_b)
        first_where=first_current_url.find('n')
        first_current_url=first_current_url[:first_where]
        first_current_url=first_current_url+'n='+str(first_pagenum*50)
        #first_soup=bs4.BeautifulSoup(res.content,'lxml')
        topic_index=0
        for url_1 in list_b:
            g.write("*****-*****-*****-*****-*****\n")
            g.write("贴子标题：\t")
            g.write(topic_list[topic_index])
            g.write('\n')
            current_url="http://tieba.baidu.com"+str(url_1)+'?pn=1'
            pagenum=1
            maxnum=5
            #max_current=5
            while(pagenum<=maxnum):
                g.write('---------------pg='+str(pagenum)+'------------------------------------\n')
                res=requests.get(current_url)
                res.raise_for_status()
                soup=bs4.BeautifulSoup(res.content,'lxml')
                soup.prettify()
                #遍历当前页面的所有楼层，打印。
                list_d=soup.find_all('cc')#,'d_post_content j_d_post_content  clearfix')
                if(soup.find('li','l_reply_num')is None):
                    maxnum=1
                else:
                    maxnum=int(soup.find('li','l_reply_num').find_all('span')[1].get_text())
                for text in list_d:
                    g.write(text.div.get_text()[12:]+'\n')
                pagenum=pagenum+1
                #之后找到下一页的url，遍历下一页的所有楼层，打印。重复循环
                where=current_url.find('?')
                current_url=current_url[:where]
                current_url=current_url+'?pn='+str(pagenum)
                #print(current_url)
            topic_index=topic_index+1
            g.write('\n')

#以下分词并统计频率

import sys
#reload(sys)

#sys.setdefaultencoding('utf-8')

import jieba
import jieba.analyse
import xlwt #写入Excel表的库
stop_list=['pg','子标题']
if __name__=="__main__":

    wbk = xlwt.Workbook(encoding = 'ascii')
    sheet = wbk.add_sheet("wordCount")#Excel单元格名字
    word_lst = []
    key_list=[]
    freq_list=[]
    times_list=[]
    for line in open('tieba.txt','r',encoding='utf8'):#1.txt是需要分词统计的文档

        item = line.strip('\n\r').split('\t') #制表格切分
        # print item
        tags = jieba.analyse.extract_tags(item[0]) #jieba分词
        for t in tags:
            word_lst.append(t)

    word_dict= {}
    with open("wordCount.txt",'w',encoding='utf8') as wf2: #打开文件
        wf2.write("关键词\t频数\t频率\t\n")
        for item in word_lst:
            if item not in word_dict: #统计数量
                word_dict[item] = 1
            else:
                word_dict[item] += 1
        orderList=list(word_dict.values())
        orderList.sort(reverse=True)
        # print orderList
        total=0
        for key in word_dict:
            total=total+word_dict[key]
        #print(str(total))
        for i in range(len(orderList)):
            for key in word_dict:
                if key not in stop_list:
                    if word_dict[key]==orderList[i]:
                        freq=100.0*word_dict[key]/total
                        wf2.write(key+'\t'+str(word_dict[key])+'\t'+'%.2f'%(freq)+'%\n') #写入txt文档
                        key_list.append(key)
                        freq_list.append(freq)
                        times_list.append(word_dict[key])
                        word_dict[key]=0
        
    sheet.write(0,0,label = '关键词')
    sheet.write(0,1,label = '频数')
    sheet.write(0,2,label = '频率')
    for i in range(len(key_list)):
        sheet.write(i+1, 2, label = "%.3f"%(freq_list[i])+'%')
        sheet.write(i+1, 1, label = "%d"%(times_list[i]))
        sheet.write(i+1, 0, label = key_list[i])
    wbk.save('wordCount.xls') #保存为 wordCount.xls文件
