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
        self.member_data={}
        self.obj_names=[]
        self.obj_list=[]
        self.final_links={}
        
    def start_analysis(self,options):
        CAST.debug('Hello World!!')
    
    def start_type(self, _type):
        self.member_data={}
    
    def start_member(self, member):
        for i in member.get_positions():
            bl=i.get_begin_line()
            el=i.get_end_line()
            d={member:[bl,el]}
            self.member_data.update(d)
               
    def end_type(self, _type):
            path = _type. get_position().get_file().get_path() 
            filename=_type.get_name()
            CAST.debug("Filename is ..."+filename)
            self.obj_names,self.final_links,self.obj_list=parser(path,filename,_type,self.member_data)
            '''if(len(self.obj_names)!=0 and len(self.final_links)!=0 and len(self.obj_list)!=0):
                CAST.debug(str(self.obj_names))
                for key,val in self.final_links.items():
                            key_index=self.obj_names.index(key)
                            for i in val:
                                i_index=self.obj_names.index(i)
                                link=create_link('useLink',self.obj_list[key_index], self.obj_list[i_index])
                                CAST.debug(self.obj_names[key_index]+"-->"+self.obj_names[i_index])'''
           
    def end_analysis(self):
        if(len(self.obj_names)!=0 and len(self.final_links)!=0 and len(self.obj_list)!=0):
                CAST.debug(str(self.obj_names))
                for key,val in self.final_links.items():
                            key_index=self.obj_names.index(key)
                            for i in val:
                                i_index=self.obj_names.index(i)
                                link=create_link('useLink',self.obj_list[key_index], self.obj_list[i_index])
                                CAST.debug(self.obj_names[key_index]+"-->"+self.obj_names[i_index])
    
           
        
