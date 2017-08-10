import re
from cast.analysers import CustomObject, create_link
import cast.analysers.log as CAST

obj_names=[]
obj_list=[]
temp={}
final_links={}

def find_instance_of_tags(var,member_data,filename,typename,_type,count,count_list):            #Finding instances of a type
    flag=0
    a=var.split(',')                                                                            #Splitting multiple instances in a single declaration
    for i in range(len(a)):
        if('=' in a[i]):
            s=a[i][:a[i].index('=')]
            a[i]=s.strip()
    for key,val in member_data.items():
        if(count>val[0] and count<val[1]):
            flag=1
            for item in a:
                create_obj(filename, typename, item,key,count,count_list)                       #creating objects with parent as the method if found inside a method
            break
    if(flag==0):
        for item in a:
                create_obj(filename, typename, item,_type,count,count_list)                     #creating objects with parent as class if it is not within any method

def update_link(topic,var):                                                                     #updating the links to establish link between Producer and Queue and eliminating Producer Record
    if(topic != None):
        if(topic in final_links):                                        
            for key,val in final_links.items():
                if key==topic:
                    if(var not in val):
                        val.append(var)
        else:
            final_links.update({topic:[var]})   

def find_str(cont,m2):                                                                          #String resolution within the method
    rev=cont[::-1]                                                                              #Contents are reversed to find most recent value
    pat="\w*\s+"+m2+"\s*=\w*"
    for j in rev:
        if(re.search(pat,j)):
            m1=j.split(m2,1)[1]
            if(',' in m1):
                    m2=m1[m1.index('=')+1:m1.index(',')]
                    return m2.strip()
            if(';' in m1):
                    m2=m1[m1.find('"'):m1.index(';')]
                    return m2.strip()

def find_in_class(cont,member_data,m2):                                                         #String resolution among class variables
    CAST.debug("Trying to find in class")
    pat="\w*\s+"+m2+"\s*=\w*"
    key_list=list(member_data.keys())
    for i in key_list:
        if(i.get_name()==m2):
            bm=member_data[i][0]
            if(bm<len(cont)):
                if(re.search(pat,cont[bm-1].strip())):
                    m1=cont[bm-1].split(m2,1)[1]
                    if(',' in m1):
                            m2=m1[m1.index('=')+1:m1.index(',')]
                            return m2.strip()
                    if(';' in m1):
                            m2=m1[m1.find('=')+1:m1.index(';')]
                            return m2.strip()

def create_obj(filename,typename,varname,parent,count,count_list):                           #Function to create objects
    if(filename+"_"+typename+"_"+varname+"_object" not in obj_names):
        anObject = CustomObject()
        CAST.debug("Object name is "+filename+"_"+typename+"_"+varname+"_object"+" Parent as :"+str(parent))
        anObject.set_name(filename+"_"+typename+"_"+varname+"_object")
        anObject.set_parent(parent)
        anObject.set_fullname(filename+"_"+typename+"_"+varname+"_object")
        anObject.set_type("MOM_"+typename)
        anObject.save()
        anObject_id = anObject._id
        count_list.update({filename+"_"+typename+"_"+varname+"_object":count})            
        obj_names.append(filename+"_"+typename+"_"+varname+"_object")   
        obj_list.append(anObject)
        if(typename!="Topic"):
            link=create_link("useLink",parent,anObject);
            CAST.debug("Parent link with ..."+str(parent)+"-->"+filename+"_"+typename+"_"+varname+"_object")
        
def parser(path,filename,_type,member_data):
    pattern='\w*Producer\w*|\w*ProducerRecord\w*|\w*KafkaConsumer\w*|\w*.subscribe\w*|\w*.send\w*|\w*KeyedMessage\w*'              #Finding the tags
    imp_pat='import\s*org.apache.kafka\w*'
    count =0
    kafka= False
    count_list={}  
    fin = open(path,'r')
    cont = fin.readlines()
    file_contents=[]
    cmt=False
    for line in cont:                                                                                                           #Removing multi line comments
        if(cmt):
            if(line.strip().endswith("*/")):
                cmt=False
        elif(line.strip().startswith("/*")):
            file_contents.append("*")
            cmt=True
        else:
            file_contents.append(line)    
    fin.seek(0)
    for line in file_contents:
        count=count+1
        if(re.match(imp_pat, line.strip())):                                                                                    #Checking import statements
            kafka=True
        if(kafka==True):
            if not line.strip().startswith('import') and not line.strip().startswith('//'):                                     #Eliminating single line comments ,import statements and class declarations
                if 'class' not in line.strip().split():                                                         
                    if re.search(pattern,line.strip()):                                        
                        if(re.search(pattern,line).group()).strip()=="KafkaConsumer":                                           #Searching for the tag KafkaConsumer
                            if(re.match("\s*KafkaConsumer\s*", line)):
                                var=line[line.find('>')+1:line.find(';')].strip()
                                find_instance_of_tags(var, member_data,filename,"KafkaConsumer",_type,count,count_list)         #Finding instances of KafkaConsumer                               
                                
                        if(re.search(pattern,line).group()).strip()=="Producer":                                                #Searching for tag Producer
                            if(re.search("\w*\s+Producer<\s*",line)):
                                var=line[line.find('>')+1:line.find(';')].strip()
                                find_instance_of_tags(var, member_data,filename,"Producer",_type,count,count_list)              #Finding instances of Producer                  
                               
                        if((re.search(pattern,line).group()).strip()=="ProducerRecord" or (re.search(pattern,line).group()).strip()=="KeyedMessage"):         #Searching for tag ProducerRecord                 
                            if((re.search("\s*ProducerRecord<\s*",line)) or (re.search("\s*KeyedMessage<\s*",line))):
                                found_in_method=0
                                var=line[line.find('>')+1:line.find('=')].strip()                               
                                l1=line.rsplit('=',1)[1]                                                        
                                l2=l1.partition('(')[-1].partition(',')[0]
                                m2=l2                                      
                                for key,val in member_data.items():
                                    if(count>val[0] and count<val[1]):                                                          #Searching for the topic name within the method
                                        CAST.debug("Searching in method "+str(key))
                                        if(l2[0]=='"' and l2[len(l2)-1]=='"'):                                                  #If topic name is hard coded            
                                            create_obj("","Topic", l2,key,-1,count_list)
                                            temp.update({var:["_Topic_"+l2+"_object"]}) 
                                            found_in_method=1   
                                            break  
                                        else:
                                            while(l2[0]!='"'):                                                                  #If topic name is present within the method
                                                l2=find_str(cont[val[0]:count],l2)
                                                if(l2==None):
                                                    break
                                                if(l2[0]=='"'):
                                                    create_obj("","Topic",l2,key,-1,count_list)
                                                    temp.update({var:["_Topic_"+l2+"_object"]}) 
                                                    found_in_method=1
                                                    break
                                if(found_in_method==0):                                                                         #Searching for topic name within the class
                                    while(m2[0].strip()!='"'):
                                        l2=m2
                                        m2=find_in_class(cont[:count],member_data,m2)
                                        if(m2==None):                                                                           #If not declared
                                            CAST.debug(l2 +" Not declared")
                                            create_obj("","Topic","valueOf("+l2+")",key,-1,count_list)                          #Creating object of the variable found
                                            temp.update({var:["_Topic_valueOf("+l2+")_object"]}) 
                                            break
                                        if(m2[0]=='"'):                                                                         #If found in class
                                            create_obj("","Topic",m2,key,-1,count_list)
                                            temp.update({var:["_Topic_"+m2+"_object"]}) 
                                            break
                                        
                                                                       
                        if('.send' in re.search(pattern,line).group()):                                                         #Searching for tag .send
                                tag_name=re.search(pattern, line).group()                                     
                                prod=tag_name[:tag_name.find('.')]                                              
                                p=filename+"_Producer_"+prod+"_object"                    
                                prod_rec=line[line.find('(')+1:line.find(')')]                                  
                                if(prod_rec.strip().startswith("new ProducerRecord<") or prod_rec.strip().startswith("new KeyedMessage<")):                         
                                    t=prod_rec[prod_rec.index('(')+1:]
                                    topic=t[:t.index(',')].strip()                                              
                                    create_obj("","Topic",topic, _type, -1, count_list)
                                    if(p in final_links):
                                        for key,val in final_links.items():
                                            if(key==p):
                                                if(topic not in val):
                                                    val.append("_Topic_"+topic+"_object")
                                    else:
                                        final_links.update({p:["_Topic_"+topic+"_object"]})
                                elif(prod_rec in temp):                                                           
                                    if(p in final_links):
                                        for key,val in final_links.items():
                                            if key==p:
                                                for i in temp[prod_rec]:
                                                    val.append(i)
                                    else:
                                        final_links.update({p:temp[prod_rec]})                                 
                        
                        if('.subscribe' in re.search(pattern,line).group()):                                                    #Searching for tag .subscribe
                            found_in_method=0
                            tag_name=re.search(pattern,line).group()  
                            var=tag_name[:tag_name.index('.')]                                              
                            var1=filename+"_KafkaConsumer_"+var+"_object"                                           
                            l1=line[line.rfind('(')+1:line.find(')')].strip()                                   
                            t=l1.split(',')
                            for key,val in member_data.items():
                                if(count>val[0] and count<val[1]):                                                              #Searching for the topic name within the method
                                    CAST.debug("Searching in method "+str(key))
                                    for l1 in t:
                                        m2=l1
                                        l1=l1.strip()
                                        if(l1[0]=='"' and l1[len(l1)-1]=='"'):                                                  #If topic name is hard coded        
                                            create_obj("","Topic", l1,key,-1,count_list)
                                            m3="_Topic_"+l1+"_object"
                                            found_in_method=1
                                            update_link(m3, var1)
                                        elif(l1[0]!='"' and l1[len(l1)-1]!='"'):                                                #Searching for topic name within the method
                                            while(l1[0]!='"'):
                                                l1=find_str(cont[val[0]:count],l1)
                                                if(l1==None):
                                                    found_in_method=0
                                                    break
                                                if(l1[0]=='"'):
                                                    create_obj("","Topic",l1,key,-1,count_list)
                                                    m3="_Topic_"+l1+"_object"
                                                    update_link(m3, var1)
                                                    found_in_method=1
                                                    break
                                        if(found_in_method==0):                                                                 #Searching in the class
                                            while(m2[0].strip()!='"'):
                                                l2=m2
                                                m2=find_in_class(cont[:count],member_data,m2)
                                                if(m2!=None):
                                                    if(m2[0]=='"'):                                                             #If found in the class
                                                        create_obj("","Topic",m2,key,-1,count_list)
                                                        m3="_Topic_"+m2+"_object"
                                                        update_link(m3, var1) 
                                                        break
                                                else:
                                                        CAST.debug(l2+" Not declared")                                          #If not declared
                                                        create_obj("","Topic","valueOf("+l2+")",key,-1,count_list)
                                                        m3="_Topic_valueOf("+l2+")_object"
                                                        update_link(m3, var1) 
                                                        m3=None
                                                        break
    return obj_names,final_links,obj_list
    
