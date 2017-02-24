import urllib,urllib2
import praw
import time 
import sys, os
from bs4 import BeautifulSoup
import xml.etree.ElementTree
import string, requests
printable = set(string.printable)

#dependancies
'''
http://www.ntsb.gov/_layouts/ntsb.aviation/brief.aspx?ev_id= #link to report info with provided id
http://app.ntsb.gov/aviationquery/Download.ashx?type=csv #link for database.txt

#HTML of report info
ctl00_PlaceHolderMain_lblNarrAcc
div id="ctl00_PlaceHolderMain_divNarrNonTerminalFont">
    <span id="ctl00_PlaceHolderMain_lblNarrAcc
'''
verbose=True

record_from=2016 #year to start recording

def download_with_progress(link,file_name):
    with open(file_name, "wb") as f:
        print "Downloading %s" % file_name
        response = requests.get(link, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]%s" % ('|' * done, ' ' * (50-done),str(done*2)+'%' ) )    
                sys.stdout.flush()


if len(sys.argv)>1 and (sys.argv[1]=='update' or sys.argv[1]=='-u' or sys.argv[1]=='u'):
    print 'Starting download'
    download_with_progress("http://app.ntsb.gov/aviationquery/Download.ashx?type=csv", "AviationData.txt")
    print '    Download complete'

def save_id_database():
    open('id_database.txt','w').write('\n'.join(id_database))

def save_post_id(post_id):
    open('post_id_database.txt','a').write(post_id+'\n')

def post_incident(data,catagories):
    global subreddit
    text_body=[]
    x=0
    end_count=0
    page = requests.get(str('https://www.ntsb.gov/_layouts/ntsb.aviation/brief.aspx?ev_id='+data[0]).strip(), verify=False).text[:]
    soup = BeautifulSoup(page.replace('<p>',' ').replace('</p>',' '), "lxml")
    soup.prettify()

    for anchor in soup.findAll('span', {"id": "ctl00_PlaceHolderMain_lblNarrAcc"}):
        for a in anchor:
            if (a.string is None):
                a.string = '\n'
        all_text=filter(lambda x: x in printable, anchor.get_text()) 
        body_text = all_text.decode('utf-8').encode("ascii","ignore")

        if body_text=='\n':
            page = requests.get(str('https://www.ntsb.gov/_layouts/ntsb.aviation/brief.aspx?ev_id='+data[0]).strip(), verify=False).text[:]
            soup = BeautifulSoup(page.replace('<p>',' ').replace('</p>',' '), "lxml")
            soup.prettify()
            for backup in soup.findAll('span', {"id": "ctl00_PlaceHolderMain_lblNarrAcc"}):
                all_text=filter(lambda x: x in printable, backup.get_text())
                body_text = all_text.encode("ascii","ignore")

        print 'Appending'
        text_body.append(body_text.decode('utf-8').encode("ascii","ignore"))
    text_body.append(('\n\n|Category|Data|Category|Data|Category|Data|\n|-----------:|:------------|-----------:|:------------|-----------:|:------------\n').decode('utf-8').encode("ascii","ignore"))
    for i in catagories: #go over each catagory and print data
        if end_count==2:
            ending='\n'
            end_count=-1
        else:
            ending=''
        text_body.append(('|'+i.strip()+':|'+data[x]+ending).decode('utf-8').encode("ascii","ignore"))
        x+=1
        end_count+=1
    text_body.append(('\n\nhttp://www.ntsb.gov/_layouts/ntsb.aviation/brief.aspx?ev_id='+data[0]).decode('utf-8').encode("ascii","ignore")) #post incident info

    #generate title
    title='['+data[10]+'] ['+data[3]+'] '+data[14]+' '+data[15].strip()+', '+data[4].replace(',','/')

    #SUBMIT THE POST
    if verbose: print '    Submitting post'
    title=filter(lambda x: x in printable, title)
    post_id = subreddit.submit(title=title.decode('utf-8').encode("ascii","ignore"), selftext=''.join(text_body)) #command,PostID,DecryptionID
    save_post_id(post_id.id)
    if verbose: print '        Post Submitted succesfully\n'

login_file=open('login.txt','r')
REDDIT_USERNAME = login_file.readline().strip('\n')
REDDIT_PASS = login_file.readline().strip('\n')
user_agent = login_file.readline().strip('\n')
if verbose: print 'Logging in as: '+REDDIT_USERNAME
r = praw.Reddit(user_agent = user_agent,client_id=login_file.readline().strip('\n'),client_secret=login_file.readline().strip('\n'),username=REDDIT_USERNAME,password=REDDIT_PASS)
if verbose: print '    Login Succesful\n'
subreddit_name=login_file.readline().strip('\n')
subreddit = r.subreddit(subreddit_name)
subscriber_count = subreddit.subscribers
print 'Subscriber Count[',subscriber_count,']'

id_database=[]
for line in open('id_database.txt','r'):
    id_database.append(line.strip('\n'))
titles=[]
for line in open('AviationData.txt','r'):
    titles=line.rstrip().split('|')
    titles.pop()
    break
update_count=0
for line in reversed(open("AviationData.txt").readlines()): #read database
    current_data=line.rstrip().split('|')
    try:
        if current_data[0] not in id_database and int(current_data[3].split('/')[2])>=record_from: #if a new incident is found and its after/is record date
            print current_data[0]
            post_incident(current_data, titles) #post new incident
            #add to database
            id_database.append(current_data[0])
            save_id_database()
            update_count+=1
    except Exception,e: 
        print str(e)
        print 'Invalid data!'
#update sidebar
sidebar_contents = subreddit.description 
time_string = str(time.localtime(time.time())[2]).zfill(2)+'/'+str(time.localtime(time.time())[1]).zfill(2)+'/'+str(time.localtime(time.time())[0])
sidebar_contents = sidebar_contents[:-10]+time_string
subreddit.mod.update(description=sidebar_contents)
update_count_text = 'Scan complete: Added '+str(update_count)+' incidents!'
print update_count_text

#make a report to desktop
os.chdir(os.path.join(os.path.expanduser('~'), 'Desktop')) #go to desktop
report_file = open('NTSB_Report.txt','w')
report_file.write(update_count_text)
report_file.write('\n'+time_string)
report_file.write('\nSubs: '+str(subscriber_count))
report_file.close()        
