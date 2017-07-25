from cast.analysers import CustomObject, create_link
import cast.analysers.jee
import cast.analysers.log as CAST
from MqParser import parser

class MyExtension(cast.analysers.jee.Extension):
    
    def __init__(self):
        self.objNlist=[]                                                     # for storing object's names
        self.objs = []                                                       # for storing objects
        self.bookmarks = {}                                                  # for storing Method's positions

    def start_analysis(self,_type):
        CAST.debug(' Hello World!! ')
        
    def createObj(self,obj,name,parent,fullname,Type):                       # function to create an object
        obj.set_name(name)
        obj.set_parent(parent)
        obj.set_fullname(fullname)
        obj.set_type(Type)
        obj.save()
        CAST.debug(str(obj.name))      
        
    def start_member(self, member):  
        if "'cast.analysers.Method'" in str(type(member)):
            self.bookmarks[member] = (member.get_positions())                 # getting positions of Method
            
    def end_type(self, _type):
        name=_type.get_name()                                                 # fetching name of class or interface
        path = _type. get_position().get_file().get_path() 
        CAST.debug("-----"+str(path)+"-----")                                 # fetching path of required file
        self.objNlist=[]
        self.objs = []
        dictP= parser(path)
        CAST.debug(" Creating Objects:    ")                                  # Creating objects for producer, consumer variables and queue name
        for key in dictP.keys():
            if "MessageProducer" in dictP[key][0] or "JMSProducer" in dictP[key][0] or "QueueSender" in dictP[key][0] or "TopicPublisher" in dictP[key][0]:
                o = CustomObject()
                self.createObj(o,name+"_"+str(key),_type,"obj"+str(key),"MOM_Producer")
                self.objNlist.append(key)
                self.objs.append(o)
            elif "TopicSubscriber" in dictP[key][0] or "JMSConsumer" in dictP[key][0] or "MessageConsumer" in dictP[key][0] or "QueueReceiver" in dictP[key][0]:
                o = CustomObject()
                self.createObj(o,name+"_"+str(key),_type,"obj"+str(key),"MOM_Consumer")
                self.objNlist.append(key)
                self.objs.append(o)
            if dictP[key][-1] not in self.objNlist:
                p = CustomObject()
                self.createObj(p,name+"_"+str(dictP[key][-1]),_type,"obj"+str(key),"MOM_Queue")
                self.objNlist.append(str(dictP[key][-1]))
                self.objs.append(p)   
        CAST.debug(" Creating Links:    ")                 
        for bk in self.bookmarks.keys():                                       # for linking Methods with objects belonging to them
            for key in dictP.keys():
                x,y = self.bookmarks[bk][0].get_begin_line() , self.bookmarks[bk][0].get_end_line()
                if dictP[key][1] in range(x,y+1):
                    obj1 = bk
                    obj2 = self.objs[self.objNlist.index(key)]
                    create_link('callLink',obj1,obj2)
                    CAST.debug(str(obj1)+" --links with-- "+obj2.name)
        for key in dictP.keys():                                               # for linking objects created
            obj1 = self.objs[self.objNlist.index(key)]
            obj2 = self.objs[self.objNlist.index(dictP[key][-1])]
            if "MessageProducer" in dictP[key][0] or "QueueSender" in dictP[key][0] or "JMSProducer" in dictP[key][0] or "TopicPublisher" in dictP[key][0]:
                create_link('callLink', obj1, obj2)
                CAST.debug(obj1.name+" --linked with-- "+obj2.name)
            else:
                create_link('callLink', obj2, obj1)
                CAST.debug(obj2.name+" --linked with-- "+obj1.name)   
        self.bookmarks={}    

    def end_analysis(self):
        CAST.debug(" Bye! ")
    
if __name__ == '__main__':
    pass
