import pandas as pd
import json, os
from os import path
import tensorflow as tf

class PredictModel:
    def __init__(self):
        self.config_path = "./predict_folder_config.json"
        with open('./import_data/label.json') as f:
            label_dict = json.load(f)
        self.model_list = list(label_dict.values())[:-1]
        self.msci_esg = {'Environment': ['Biodiversity and Land Use', 'Carbon Emissions', 'Climate Change Vulnerability', 'Electronic Waste', 'Financing Environmental Impact', 'Opportunities in Clean Tech', 'Opportunities in Green Building', 'Opportunities in Renewable Energy', 'Packaging Material and Waste', 'Product Carbon Footprint', 'Raw Material Sourcing', 'Toxic Emissions and Waste', 'Water Stress'], 'Social': ['Access to Communications', 'Access to Finance', 'Access to Health Care', 'Chemical Safety', 'Community Relations', 'Controversial Sourcing', 'Financial Product Safety', 'Health and Demographic Risk', 'Health and Safety', 'Human Capital Development', 'Labor Management', 'Opportunities in Nutrition and Health', 'Privacy and Data Security', 'Product Safety and Quality', 'Responsible Investment', 'Supply Chain Labor Standards'], 'Governance' : ['Accounting', 'Board', 'Business Ethics', 'Ownership and Control', 'Pay', 'Tax Transparency'] }
        with open(self.config_path) as f:
            self.config_dict = json.load(f)

    def get_config(self):
        with open(self.config_path) as f:
            config_dict = json.load(f)
        return config_dict
    
    def set_config(self, config_dict):
        with open(self.config_path, 'w') as f:
            json.dump(config_dict,f)
        print("Set Config Success")
        
    # Sometime the bert script will crash for no reason, and it will work after running again
    def run_model(self,file_name):
        fail_list = []
        for model in self.model_list:
            if not path.exists("{}/{}".format(self.config_dict['output_dir'],model)):
                print("Not exist")
                os.system('mkdir \"{}/{}\"'.format(self.config_dict["output_dir"],model))
            bert_script = ["python", '{}'.format(self.config_dict["script_name"]), '--task_name=class_2', '--do_predict=True', 
                           '\"--data_dir={}/{}\"'.format(self.config_dict["data_dir"],file_name), '\"--vocab_file={}/vocab.txt\"'.format(self.config_dict["pretrain_model_dir"]),
                           '\"--bert_config_file={}/bert_config.json\"'.format(self.config_dict["pretrain_model_dir"]),
                           '\"--init_checkpoint={}/{}/{}\"'.format(self.config_dict["finetune_mode_dir"],model,self.config_dict["checkpoint"]),
                           '--max_seq_length={}'.format(self.config_dict["max_seq_length"]),
                           '\"--output_dir={}/{}\"'.format(self.config_dict["output_dir"],model),
                           '\"--output_tsv_name={}\"'.format(file_name)
                          ]
            print(' '.join(bert_script))
            if os.system(' '.join(bert_script)) != 0:
                fail_list.append(model)

        if len(fail_list) == 0:
            return 'All model predict Success'
        else:
            return "{} fail!".format('/'.join(fail_list))
    
    def combine_predict_result(self, file_name):
        report_df = pd.DataFrame()
        for key_issue in self.model_list:
            tmp_df = pd.read_csv('{}/{}/{}'.format(self.config_dict["output_dir"],key_issue,file_name),sep='\t', names=['No',key_issue])
            if report_df.empty:
                report_df = tmp_df[key_issue].to_frame(name=key_issue)
            else:
                report_df[key_issue] = tmp_df[key_issue].values

        report_df.to_csv('{}/{}_table.csv'.format(self.config_dict["output_table_dir"], file_name[:-4])) 