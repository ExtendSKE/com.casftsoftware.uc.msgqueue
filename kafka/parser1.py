'''
Created on Jun 23, 2017
@author: GDE
'''
import re
from cast.analysers import CustomObject,Bookmark,create_link,Object,Member

obj_names=[]
obj_list=[]
temp={}
final_links={}
found=[]

def search(cont1,l2):                                                   #Function for String resolution to get the topic name
    i=0
    while(i!=len(cont1)):
            pat="\w*\s+"+l2+"\s*=\w*"
            cont=cont1[i].split(',')
            for j in cont:
                if(re.search(pat,j)):
                    if(i not in found):
                        m1=j.split(l2,1)[1]
                        if('"' in m1):
                            if(';' in m1):
                                m2=m1[m1.index('=')+1:m1.index(';')]
                                return m2.strip()
                            else:
                                m2=m1[m1.find('"'):m1.rfind('"')+1]
                                return m2.strip()
                        else:
                            if(';' in m1):
                                m2=m1[m1.index('=')+1:m1.index(';')]
                                found.append(i)
                                m2=search(cont1,m2.strip())
                                return m2
                            else:
                                m2=m1[m1.index('=')+1:]
                                found.append(i)
                                m2=search(cont1,m2.strip())
                                return m2
            i=i+1
            
def create_obj(filename,typename,varname,_type,count,count_list):                           #Function to create objects
    if(filename+"_"+typename+"_"+varname+"_object" not in obj_names):
        anObject = CustomObject()
        print("Object name is "+filename+"_"+typename+"_"+varname+"_object")
        anObject.set_name(filename+"_"+typename+"_"+varname+"_object")
        anObject.set_parent(_type)
        anObject.set_fullname(filename+"_"+typename+"_"+varname+"_object")
        anObject.set_type("MOM_"+typename)
        anObject.save()
        anObject_id = anObject._id
        count_list.update({filename+"_"+typename+"_"+varname+"_object":count})            
        obj_names.append(filename+"_"+typename+"_"+varname+"_object")   
        obj_list.append(anObject)
        
def parser(path,filename,_type):
    
    pattern='\w*Producer\w*|\w*ProducerRecord\w*|\w*KafkaConsumer\w*|\w*.subscribe\w*|\w*.send\w*|\w*KeyedMessage\w*'              #Finding the tags
    imp_pat='import\s*org.apache.kafka\w*'
    count =0
    kafka= False
    count_list={}  
    found=[]
    fin = open(path,'r')
    cont = fin.readlines()
    final_links={}
    fin.seek(0)
    for line in fin:
        count=count+1
        if(re.match(imp_pat, line.strip())):
           
            kafka=True
        if(kafka==True):
            print("Scanning file "+filename)
            if not line.strip().startswith('import') and not line.strip().startswith('//'):                     #Excluding imports and single line comments
                if 'class' not in line.strip().split():                                                         #Excluding class names
                    if re.search(pattern,line.strip()):                                        
                        
                        if(re.search(pattern,line).group()).strip()=="KafkaConsumer":                           #If tag found is KafkaConsumer
                            if(re.match("\s*KafkaConsumer\s*", line)):
                                var=line[line.find('>')+1:line.find(';')].strip()                               #Extracting variable instance of KafkaConsumer
                                a=var.split(',')                                                                #Splitting on , in case multiple instances are present
                                for i in range(len(a)):
                                    if('=' in a[i]):
                                        s=a[i][:a[i].index('=')]
                                        a[i]=s.strip()
                                for item in a:
                                    create_obj(filename, "KafkaConsumer", item,_type,count,count_list)          #Creating an object of KafkaConsumer for each instance found
                               
                        if(re.search(pattern,line).group()).strip()=="Producer":                                #If tag found is Producer
                            if(re.match("\w*\s+Producer<\s*",line)):
                                
                                var=line[line.find('>')+1:line.find(';')].strip()                               #Extracting variable instance of Producer
                                a=var.split(',')                                                                #Splitting on , in case multiple instances are present
                                for i in range(len(a)):
                                    if('=' in a[i]):
                                        s=a[i][:a[i].index('=')]
                                        a[i]=s.strip()
                                for item in a:
                                    create_obj(filename, "Producer", item,_type,count,count_list)               #Creating an object of Producer for every instance found
                                     
                        if((re.search(pattern,line).group()).strip()=="ProducerRecord" or (re.search(pattern,line).group()).strip()=="KeyedMessage"):                          #If tag found is ProducerRecord
                            if((re.search("\s*ProducerRecord<\s*",line)) or (re.search("\s*KeyedMessage<\s*",line))):
                                #print(line)
                                var=line[line.find('>')+1:line.find('=')].strip()                               #Extracting instance of ProducerRecord or KeyedMessage
                                l1=line.rsplit('=',1)[1]                                                        
                                l2=l1.partition('(')[-1].partition(',')[0]                                      #Extracting the topic name
                                if(l2[0]=='"' and l2[len(l2)-1]=='"'):              
                                    create_obj("","Topic", l2,_type,-1,count_list)                              #Creating an object for the topic
                                    m2=l2
                                else:
                                    found.append(count)
                                    m2=search(cont,l2)                                                          #Resolving the string to get the topic name
                                    create_obj("","Topic",m2,_type,-1,count_list)                               #Creating an object for topic name
                                temp.update({var:["_Topic_"+m2+"_object"]})                                     #Storing link between Producer and ProducerRecord/KeyedMessage instances temporarily
                        
                        if('.send' in re.search(pattern,line).group()):                                         #If tag found is .send
                                print(re.search(pattern,line).group()+"  "+str(count))
                                tag_name=re.search(pattern, line).group()                                     
                                prod=tag_name[:tag_name.find('.')]                                              #Getting the Producer instance
                                p=filename+"_Producer_"+prod+"_object"                    
                                prod_rec=line[line.find('(')+1:line.find(')')]                                  #Getting ProducerRecord instance or KeyedMessage instance
                                if(prod_rec.strip().startswith("new ProducerRecord<") or prod_rec.strip().startswith("new KeyedMessage<")):                         #If ProducerRecord/KeyedMessage is being initialized here
                                    t=prod_rec[prod_rec.index('(')+1:]
                                    topic=t[:t.index(',')].strip()                                              #Extracting topic name
                                    create_obj("","Topic",topic, _type, -1, count_list)                         #Creating object for topic
                                    if(p in final_links):                                                       #Establishing link between Producer and Topic
                                        for key,val in final_links.items():
                                            if(key==p):
                                                if(topic not in val):
                                                    val.append("_Topic_"+topic+"_object")
                                    else:
                                        final_links.update({p:["_Topic_"+topic+"_object"]})
                                elif(prod_rec in temp):                                                           #If instance of ProducerRecord/KeyedMessage is present
                                    if(p in final_links):
                                        for key,val in final_links.items():
                                            if key==p:
                                                for i in temp[prod_rec]:
                                                    val.append(i)
                                    else:
                                        final_links.update({p:temp[prod_rec]})                                  #Updating the final links
                        
                        if('.subscribe' in re.search(pattern,line).group()):                                    #If tag name is .subscribe
                            tag_name=re.search(pattern,line).group()                                            
                            l1=line[line.rfind('(')+1:line.find(')')].strip()                                   #Finding the topic names consumer is subscribed to
                            t=l1.split(',')
                            for l1 in t:
                                if(l1.strip()[0]=='"' and l1.strip()[len(l1.strip())-1]=='"'):
                                    create_obj("","Topic",l1.strip(),_type,-1,count_list)                       #Creating object for topic
                                    m2=l1
                                else:
                                    found.append(count)
                                    m2=search(cont,l1.strip())                                                  #Resolving the string the get topic name
                                    create_obj("","Topic",m2.strip(),_type,-1,count_list)                       #Creating object for topic name
                                m3="_Topic_"+m2.strip()+"_object"
                                var=tag_name[:tag_name.index('.')]                                              #Retrieving Consumer instance    
                                var1=filename+"_KafkaConsumer_"+var+"_object"
                                if(m3 in final_links):                                        
                                    for key,val in final_links.items():
                                        if key==m3:
                                            if(var1 not in val):
                                                val.append(var1)
                                else:
                                    final_links.update({m3:[var1]})                                             #Updating final links between Topic and Consumer
                                    
    #print("Obj list is..")
    #print(obj_names)
    #print("Final Links are..")
    #print(final_links)
    return obj_names,final_links,obj_list,count_list
    
#a=CustomObject()
#a.save()
#parser("C:\\Users\\GDE\\workspace\\com.castsoftware.kafka1\\KafkaTests\\Tests\\SimpleConsumer.java","SimpleConsumer",a)
