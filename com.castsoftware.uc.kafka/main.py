'''
Created on Jul 19, 2017
@author: GDE
'''
import cast.analysers.log as CAST
from cast.analysers import create_link
import cast.analysers.jee
from parser1 import parser
class KafkaExtension(cast.analysers.jee.Extension):
    
    def __init__(self):
       
        self.count_list={}
        self.obj_names=[]
        self.obj_list=[]
        self.final_links={}
        
    def start_analysis(self,options):
        CAST.debug('Hello World!!')
       
    def start_type(self, _type):
            path = _type. get_position().get_file().get_path() 
            CAST.debug("Path is ..."+path)
            filename=_type.get_name()
            
            self.obj_names,self.final_links,self.obj_list,self.count_list=parser(path,filename, _type)
            if(len(self.obj_names)!=0 and len(self.final_links)!=0 and len(self.obj_list)!=0):
                CAST.debug(str(self.obj_names))
                for key,val in self.final_links.items():
                            key_index=self.obj_names.index(key)
                            for i in val:
                                i_index=self.obj_names.index(i)
                                link=create_link('callLink',self.obj_list[key_index], self.obj_list[i_index])
                                CAST.debug(self.obj_names[key_index]+"-->"+self.obj_names[i_index])
        
    def start_member(self, member):
        for i in member.get_positions():
            CAST.debug(str(i))
            bl=i.get_begin_line()
            el=i.get_end_line()
            CAST.debug(str(bl)+" "+str(el))
            for key,val in self.count_list.items():
                if(val>bl and val<el):
                    obj_index=self.obj_names.index(key)
                    link=create_link('callLink', member, self.obj_list[obj_index])
                    CAST.debug(member.get_name()+"-->"+self.obj_names[obj_index])