#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 11:44:55 2018

@author: ratdeh
"""

import os
#server path
#os.chdir('/home/ec2-user/harsh/projects/mint/grid_opt')

#local path
os.chdir('/Users/maitya/Dropbox (21st Century Fox)/grid_data_single_pilot_v1')
os.listdir()
from pyomo.environ import *
import pyomo
import pyomo.opt
import pyomo.environ as pe
import logging 
import pickle
import pandas as pd
import datetime, calendar

# ------------ USER INPUT ---------------
op =1

client_lookup = {'GEN_MILS':'General Mills 3'}
client_key = 'GEN_MILS'

#target_outlay = 12874000/op # 443
#target_outlay = 12874000/op   #5
#target_GRP = 443

#target_CPRP = {'PT': 1000 ,'NPT':2000 }

#opt_mode_lkp = {0:'regular',1:'impact_push'}
#opt_mode = 0

#if opt_mode == 1:
#    shw_nm = input('Enter show name : ')

#show_outlay_share = {'Qayamat Ki Raat': 0.3}
#show_outlay_share = {'Amazon Abhiyaan': 0.15,'Kulfi Kumar Baajwala':0.15}


# STRT DT
# END DT
#inp_strt_dt = "20181117"
#inp_end_dt = "20181231"

inp_tdy_cmpt = datetime.datetime.today().strftime('%Y%m%d')

max_ad_pb = 2
ad_duration = 5 # inseconds

days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
# ------------ READ DATA ----------------

def get_show_duration(input_string, ind):
    #input_string = '04:00 - 05:00' 
    tm_1, tm_2 = input_string.split(' - ')
    tm_dt_1=datetime.datetime.strptime(tm_1,'%H:%M')
    tm_dt_2=datetime.datetime.strptime(tm_2,'%H:%M')
    tm_dlta = tm_dt_2 - tm_dt_1
    
    if ind == 1:
        return tm_dlta.seconds/60
    #output : 60.0
    elif ind == 2:
        num_sub_bkt = int(tm_dlta.seconds/60/30)
        time_collec = [tm_dt_1.strftime('%H:%M')]
        for sub_b in range(0,num_sub_bkt):
            #print(sub_b)
            #print(tm_dt_2+datetime.timedelta(minutes=(sub_b+1)*30))
            tmp_tm = tm_dt_1+datetime.timedelta(minutes=(sub_b+1)*30)
            time_collec.append(tmp_tm.strftime('%H:%M'))
        return time_collec
    #output :  ['04:00', '04:30', '05:00']
    
#get_show_duration('04:00 - 05:00',2)
    
def parse_tmbnd_buck(input_list1,start_indx):
    #input_list1 = ['13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30']
    #start_indx = 0    
    
    #combines every consequitive value separated by a ' - '
    sub_list =  input_list1[start_indx:start_indx+2]
    return str(' - '.join(sub_list))

#parse_tmbnd_buck(['13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30'],1)

def time_rank_ref(dur,rank):
    #creates pair waise labels
    temp_dict = {}
    tm_rng = get_show_duration(dur, 2)
    for item in range(0,len(tm_rng)-1):
        temp_dict[parse_tmbnd_buck(tm_rng,item)]=rank
        
    return temp_dict

#time_rank_ref('18:30 - 00:00', 'PT')
#output:
#{'18:30 - 19:00': 'PT',
# '19:00 - 19:30': 'PT',
# '19:30 - 20:00': 'PT',
# '20:00 - 20:30': 'PT',
# '20:30 - 21:00': 'PT',
# '21:00 - 21:30': 'PT',
# '21:30 - 22:00': 'PT',
# '22:00 - 22:30': 'PT',
# '22:30 - 23:00': 'PT',
# '23:00 - 23:30': 'PT',
# '23:30 - 00:00': 'PT'}

def opt_end_ver_sv():
    date_master_out2.to_csv('date_master_out2.csv')
    
    
    pickle_out = open("date_master_out2.pickle","wb")
    pickle.dump(date_master_out2, pickle_out)
    pickle_out.close()
    
    
    
    dir_check = []
    print(os.listdir())
    
    for item in os.listdir():
        if 'log_dir_' in item:
            dir_check.append(item)
    
    if len(dir_check) == 0 :
        dir_name = 'log_dir_1'
        os.mkdir(dir_name)
    else:
        ver_lst = []
        for fl in dir_check:
            
            ver_lst.append(int(fl.split('_')[-1]))
            curr_ver_num = max(ver_lst)+1
        dir_name = 'log_dir_{}'.format(str(curr_ver_num))
        os.mkdir(dir_name)
    
    list_files = []
    for item in os.listdir():
        for j in ['.bar','.log','.sol','.tim','date_master_out2.pickle','date_master_out2.csv']:
            if j in item:
                print(item)
                
                list_files.append(item)
            
    for item3 in list_files:
        os.system('mv {} {dir_name}/{}'.format(item3,item3))



    
    
#CREATE MONTHS STARTDATE AND ENDDATE
def get_mon_st_end_dt(month_name_input):
    year = int(month_name_input/100)
    month = month_name_input - year*100
    num_daysl = calendar.monthrange(year, month)[1]
    strt_dy_mon = datetime.date(year, month, 1)
    end_dy_mon = datetime.date(year, month, num_daysl)
    print('{} - {}'.format(strt_dy_mon ,end_dy_mon))
    return [strt_dy_mon,end_dy_mon]

#def date_master_create(a_dt=inp_strt_dt,b_dt=inp_end_dt):#),datai):
def date_master_create(mon_nm):
    #mon_nm = 201811
#    a_dt=inp_strt_dt
#    b_dt=inp_end_dt

    [base_strt,base_end] = get_mon_st_end_dt(mon_nm)

    #base_strt   = datetime.datetime.strptime(str(a_dt), "%Y%m%d")#.strftime("%Y-%m-%d")
    #base_end    = datetime.datetime.strptime(str(b_dt), "%Y%m%d")
    
    numdays     = base_end - base_strt 
    date_list   = [base_strt + datetime.timedelta(days=x) for x in range(0, numdays.days+1)]
    date_master = pd.DataFrame({'date':date_list})
    
    list(calendar.day_abbr)
    date_master['day_nm']       = date_master['date'].apply(lambda x: x.strftime('%a'))
    date_master['week_num']     = date_master['date'].apply(lambda x: x.isocalendar()[1])
    date_master['dy_of_week']   = date_master['date'].apply(lambda x: x.isocalendar()[2])
    date_master['date']         = date_master['date'].apply(lambda x: x.strftime('%Y%m%d'))
    
    # =============================================================================
    
    #import input sheet- basis rate card of the MONTH
    data = pd.read_csv('data/SP_Rate_Card_{}.csv'.format(str(mon_nm)))
    #data = pd.read_csv('grid_sp_input.csv')
    
    #``````````````````````````````````````````````````
    #   'data' dataframe is taken as input to this function   
    #``````````````````````````````````````````````````
    
    #rename TVR
    import numpy as np
    data.rename(columns={'TVR': 'TVR_chan'}, inplace=True)
    data['TVR_clnt'] = data['TVR_chan'].apply(lambda x : x*(1+np.random.uniform(-0.3,0.3,1)[0]))
    
    data['FP Threshold']    = data['FP Threshold'] /op
    data['Floor Price']     = data['Floor Price'] /op
     
    
    
    def get_the_days(input_string,ind):
        #print('------- {} ------'.format(input_string))    
        #input_string = '(Kasauti Zindagii Kay)-(O)-(Fri-Mon)-(20:00-20:30)-(SPSD)'
        
        dy_prsn     = [1 if i in input_string else 0 for i in days ]
        dy_collec   = [i for i in input_string.split(')-(')  if days[dy_prsn.index(1)] in i][0]
        
        #------ by this point in time DY-COLLEC is either single day or collection
        
        if ind == 0:
            # ----- GET THE NUMBER OF DAYS -------
            if '-' in dy_collec:
                #print('Multiple days')
                days_endp   = dy_collec.split('-')
                s_p         = days.index(days_endp[0].strip())+1
                e_p         = days.index(days_endp[1].strip())+1
                
                if s_p < e_p:
                    num_days = e_p - s_p + 1
                elif s_p> e_p:
                    num_days = 7 - s_p + e_p + 1
                else:
                    print('-------- ISSUE --------')
                
            else:
                #print('single day')
                num_days = 1
            
            return num_days
        
        elif ind == 1:
            # ---------- GET NAME OF THE DAYS
            if '-' in dy_collec:
                #print('Multiple days')
                days_endp   = dy_collec.split('-')
                s_p         = days.index(days_endp[0].strip())
                e_p         = days.index(days_endp[1].strip())
                
                if s_p < e_p:
                    rng             = list(range(s_p,e_p+1))
                    name_days       = [days[i] for i in rng]
                    name_days_out   = '-'.join(name_days)
                    
                elif s_p> e_p:
                    rng_a           = list(range(s_p,7))
                    rng_b           = list(range(0,e_p+1))
                    rng             = rng_b + rng_a
                    name_days       = [days[i] for i in rng]
                    name_days_out   = '-'.join(name_days)
                else:
                    print('-------- ISSUE --------')
                
            else:
                #print('single day')
                name_days_out = dy_collec
            
            return name_days_out
            
            
        #print('Number of days in this entry : {}'.format(str(num_days)))
        
        
    def get_show_name(input_string):
        #input_string = '(Kasauti Zindagii Kay)-(O)-(Mon-Fri)-(20:00-20:30)-(SPSD)'
        return input_string.split(')-(')[0][1:]
    
    def get_stream_type(input_string):
        if '(O)' in input_string:
            return 'original'
        elif '(R)' in input_string:
            return 'repeat'
        else:
            return 'others' 
    
    data['days_numb']               = data['Sales Unit'].apply(lambda x : get_the_days(x,0))
    data['days_name_collection']    = data['Sales Unit'].apply(lambda x : get_the_days(x,1))
    
    for item in days:
        data[item] = data['days_name_collection'].apply(lambda x: 1 if item in x else 0)
    
    data_2 = pd.melt(data, id_vars=['Sales Unit', 'Timeband', 'Channel Tags', 'Floor Price', 'FP Threshold',
           'CPRP', 'TVR_chan','TVR_clnt', 'days_numb', 'days_name_collection'],
            var_name="day_name", value_name="Value")
    
    data_2 = data_2[data_2.Value == 1].sort_values(['Sales Unit', 'Timeband', 'Channel Tags', 'Floor Price', 'FP Threshold',
           'CPRP', 'TVR_chan','TVR_clnt', 'days_numb', 'days_name_collection'])
    
    data_2 = data_2.drop(['Value'],axis=1)
    
    data_2['show_nm'] = data_2['Sales Unit'].apply(lambda x : get_show_name(x))
    data_2['stream_type'] = data_2['Sales Unit'].apply(lambda x : get_stream_type(x))
    
    #data['Channel Tags'].unique().tolist()
    # function get_show_duration is placed here
    
    data_2['Timeband'] = data_2['Timeband'].apply(lambda x : x.replace('24:','00:') if '24:' in x else x)
    data_2['Timeband'] = data_2['Timeband'].apply(lambda x : x.replace('25:','01:') if '25:' in x else x)    
    data_2['show_duration_mins'] = data_2['Timeband'].apply(lambda x : get_show_duration(x,1))
    data_2['sub_buckets_collec'] = data_2['Timeband'].apply(lambda x : get_show_duration(x,2))
    data_2['sub_buckets_count'] = data_2['sub_buckets_collec'].apply(lambda x : len(x)-1)
    max_bucket_span = max(data_2['sub_buckets_count'])
    
    for item in range(0,max_bucket_span):
        data_2['col_{}'.format(item)]=0
#    'sub_buckets_collec','sub_buckets_count'
    
    data_2_1 = pd.melt(data_2, id_vars=['Sales Unit',
     'Timeband',
     'Channel Tags',
     'Floor Price',
     'FP Threshold',
     'CPRP',
     'TVR_chan',
     'TVR_clnt',
     'days_numb',
     'days_name_collection',
     'day_name',
     'show_nm',
     'stream_type',
     'show_duration_mins',
     'sub_buckets_collec',
     'sub_buckets_count'],
            var_name="buck_countr", value_name="buck_ind")
    
    data_2_1 = data_2_1.drop(['buck_ind'],axis=1)
    
    data_2_1['buck_countr']=data_2_1['buck_countr'].apply(lambda x : int(x.split('_')[-1]))
    
    def drop_cols(counter, ref):
        if counter < ref:
            return 1
        else:
            return 0
    
    data_2_1['drop_cols'] = data_2_1.apply(lambda x : drop_cols(x['buck_countr'],x['sub_buckets_count']),axis=1)
    data_2_1 = data_2_1[data_2_1['drop_cols']==1]
    data_2_1 = data_2_1.drop(['drop_cols'],axis=1)
     
    data_2_1['Timeband_corr'] = data_2_1.apply(lambda x : parse_tmbnd_buck(x['sub_buckets_collec'],x['buck_countr']), axis =1)
    data_2_2 = data_2_1.drop(['sub_buckets_collec'],axis=1)
    
    data_2_2 = data_2_2.sort_values(['Sales Unit',
     'Timeband',
     'Channel Tags',
     'days_numb',
     'days_name_collection',
     'day_name',
     'show_nm',
     'stream_type'])
    
    data_2_2['Timeband'] = data_2_2['Timeband_corr']
    data_2 = data_2_2.drop(['Timeband_corr'],axis=1)
    
    # ============  timeband corrected ===================
    
    data_2['add_slots'] = data_2['show_duration_mins'].apply(lambda x : (13*x/ad_duration))
    data_2 = data_2.reset_index(drop = True)
    
    sample_shows = data_2.groupby(['show_nm','day_name']).size().reset_index().rename(columns={0:'count'})
    sample_tm = data_2.groupby(['Timeband','day_name']).size().reset_index().rename(columns={0:'count'})
    conflict = data_2[(data_2['Timeband']=='18:00 - 18:30') & (data_2['day_name']=='Thur')]
    data_2['trig_ind'] = data_2['show_nm'].apply(lambda x: 1 if x =='RODP' else 0)
    data_3 = data_2.sort_values(['Timeband','day_name','trig_ind'])
    
    data_3 = pd.merge(  data_3
                      , sample_tm
                      , left_on=['Timeband','day_name']
                      , right_on=['Timeband','day_name']
                      , how='left')
    
    
    data_4 = data_3.groupby(['Timeband','day_name']).first().reset_index()
    sample_tm2 = data_4.groupby(['Timeband','day_name']).size().reset_index().rename(columns={0:'count'})
    
    date_master = pd.merge(     date_master
                           ,    data_4
                           ,    left_on = 'day_nm'
                           ,    right_on = 'day_name'
                           ,    how = 'left')
    
    sample_tm3 = date_master.groupby(['date','Timeband','day_name']).size().reset_index().rename(columns={0:'count'})
    sample_tm3['count'].unique()
    
    def corr_chan_tag(input_string, check_day):
        #input_string= 'NPT-WD-WE'
        #check_day = 'Sat'
        if 'WD' in input_string and check_day in ['Sat','Sun']:
            output_string = input_string.replace('WD','').replace('--','-')
            
            if output_string[-1] == '-':
               output_string = output_string[:-1] 
               
        elif 'WE' in input_string and check_day in ['Mon','Tue','Wed','Thu','Fri']:
            output_string = input_string.replace('WE','').replace('--','-')
            
            if output_string[-1] == '-':
               output_string = output_string[:-1] 
               
        else:
            output_string = input_string
    
        return output_string
    
    #['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    date_master['Channel Tags_corr'] = date_master.apply(lambda x : corr_chan_tag(x['Channel Tags'],x['day_nm']),axis=1 )
    
    def week_day(input_string):
        if input_string in ['Mon','Tue','Wed','Thu','Fri']:
            return 'WD'
        elif input_string in ['Sat','Sun']:
            return 'WE'
        
    date_master['week_day_type'] = date_master['day_nm'].apply(lambda x : week_day(x))
    # ---------------- WEEK DAY TYPES are populated correctly ---------------------
    
    # ---------------- FURTHER CORRECT THE CHANNEL TAG ----------------------------
    
    def corr_chan_tag_p2(input_string):
        if 'WD' in input_string:
                
            output_string = input_string.replace('WD','').replace('--','-')
                
            if output_string[-1] == '-':
               output_string = output_string[:-1] 
               
        elif 'WE' in input_string:
            output_string = input_string.replace('WE','').replace('--','-')
                
            if output_string[-1] == '-':
               output_string = output_string[:-1] 
        else:
            output_string = input_string
           
        return output_string
    
    date_master['Channel Tags_corr'] = date_master['Channel Tags_corr'].apply(lambda x: corr_chan_tag_p2(x))
    
    
    date_master['show_duration_mins'] = date_master['Timeband'].apply(lambda x : get_show_duration(x,1))
    date_master['add_slots'] = date_master['show_duration_mins'].apply(lambda x : 78*x/60)
#    date_master['sub_buckets_collec'] = date_master['Timeband'].apply(lambda x : get_show_duration(x,2))
#    date_master['sub_buckets_count'] = date_master['sub_buckets_collec'].apply(lambda x : len(x)-1)
    
    #date_master['Channel Tags_corr'].unique()
    #chk1 = date_master[date_master['Channel Tags_corr']=='PT-NPT-WE']
    #chk2 = date_master[date_master['show_nm']=='Dance Plus-4']
    
    # ----------- time rank reference ---------------------------------------------
    #PT

    
    pt_ref = time_rank_ref('18:30 - 00:00', 'PT')
    npt_ref = time_rank_ref('07:00 - 18:30', 'NPT')
    #pt_ref = time_rank_ref('18:30 - 00:00', 'CPT')
    dh_ref = time_rank_ref('00:00 - 07:00', 'DH')
    tm_ref={}
    tm_ref.update(time_rank_ref('18:30 - 00:00', 'PT'))
    tm_ref.update(time_rank_ref('07:00 - 18:30', 'NPT'))
    tm_ref.update(time_rank_ref('00:00 - 07:00', 'DH'))
    
    date_master['Channel Tags_corr2'] = date_master['Timeband'].apply(lambda x: tm_ref[x])
    date_master['Channel Tags_orgnl'] = date_master['Channel Tags']
    date_master['Channel Tags'] = date_master['Channel Tags_corr2']
    
    # =============================================================================
    # Data prep complete
    
    date_master = date_master.drop(['days_name_collection','Channel Tags_corr','Channel Tags_corr2','Channel Tags_orgnl'],axis=1)
    
    return date_master

#==============================================================================
    
# CLIENT LEVEN INPUT CREATE
# =============================================================================
#   CREATING THE CLIENTS ASK 

#data = pd.read_csv('grid_sp_input.csv')
deal_data = pd.read_csv('data/grid_proposal_data.csv')
deal_data['CH_TVR'] = pd.to_numeric(deal_data['CH_TVR'], errors='coerce')
deal_data['CL_GRP'] = deal_data['CL_GRP'].fillna(deal_data['CH_GRP']) 
deal_data['CH_CPRP'] = deal_data['Final_Outlay']/deal_data['CH_GRP']
deal_data['CL_CPRP'] = deal_data['Final_Outlay']/deal_data['CL_GRP']

deal_data.columns
#find combination of <channel_name, advertizer_name, sales_app_deal_ID>
#loop on above combination and execute the optimization 

deal_data['sls_deal_key'] = deal_data.apply(lambda x : '|'.join([x['CHANNEL_NAME'],x['ADVERTISER_NAME'],str(x['SALES APP_DEAL_ID'])]),axis=1)
deal_data['sls_deal_key'] = deal_data['sls_deal_key'].apply(lambda x : x.replace(' ','_'))

sls_deal_key_lst = deal_data['sls_deal_key'].unique().tolist()

#create the dictionary - data, regular/impact,show_outlay_share
#data_repo
def mon_list(bs_dt_1t,bs_dt_2t,case=1):
    numdays     = bs_dt_2t - bs_dt_1t
    date_list   = [bs_dt_2t - datetime.timedelta(days=x) for x in range(0, numdays.days)]
    if case == 0:
        year_mon_list = list(set(sorted([int(i.strftime("%Y%m")) for i in date_list if int(i.strftime("%Y%m")) > int(bs_dt_1t.strftime("%Y%m"))]  )))
    elif case ==1:
        year_mon_list = list(set(sorted([int(i.strftime("%Y%m")) for i in date_list if int(i.strftime("%Y%m")) >= int(bs_dt_1t.strftime("%Y%m"))]  )))
    return year_mon_list

#mon_list(bs_dt_1,bs_dt_2)
client_lookup = {'GEN_MILS':'General Mills 3'}
#client_key = 'GEN_MILS'

def main_module(sample):   
    sample =  'Star_Plus|Itc_Group|3092'    
    #sample = 'Star_Plus|Matrimony.Com|1988'
    print('------------ {} --------------'.format(sample))
    sample_set  = deal_data[deal_data['sls_deal_key']==sample]

    sample_adv_name = sample_set['SALES APP_DEAL_NAME'].unique()[0]
    client_key = str(sample_set['SALES APP_DEAL_ID'].unique()[0])
    client_lookup.update({client_key:sample_adv_name})
    
    inp_strt_dt = sample_set['PROPOSAL_START_DATE'].unique()[0]
    inp_end_dt  = sample_set['PROPOSAL_END_DATE'].unique()[0]
    
    inp_strt_dt = datetime.datetime.strptime(inp_strt_dt, "%d/%m/%y").strftime("%Y%m%d")
    inp_end_dt  = datetime.datetime.strptime(inp_end_dt, "%d/%m/%y").strftime("%Y%m%d")
    
    
    check_dt = datetime.datetime.strptime(inp_end_dt, "%Y%m%d")
#    if check_dt <= datetime.datetime.strptime('20190101', "%Y%m%d"):
    if True:
        
        target_outlay   =   sample_set['Final_Outlay'].sum()
        target_grp      =   sample_set['CL_GRP'].sum()
        print(target_grp)
    #    if target_grp == 0:
    #        continue
    #        
        
        target_cprp     =   sum(sample_set['Final_Outlay']*sample_set['CL_GRP'])/sum(sample_set['CL_GRP'])
        
        input_repo = {
                      'target_outlay'   :target_outlay,
                      'target_grp'      :target_grp,
                      'target_cprp'     :target_cprp,
                      'inp_strt_dt'     :inp_strt_dt,
                      'inp_end_dt'      :inp_end_dt
                      }
            
        outl_shr = sample_set[sample_set['CH_Imp_Reg']=='impact'][['Sales Unit','Final_Outlay']].groupby(['Sales Unit'])['Final_Outlay'].sum().reset_index()
        
        if outl_shr.shape[0] >0:
            opt_mode = 1
            outl_shr['share'] = outl_shr['Final_Outlay']/sum(sample_set['Final_Outlay'])
            outl_shr['Sales Unit'] = outl_shr['Sales Unit'].apply(lambda x : x.split(')-(')[0][1:])
            outl_shr['share'] = outl_shr['share'].apply(lambda x: round(x,2))
            
            show_outlay_share = {}
            
            for i in range(0,outl_shr.shape[0]):
                show_outlay_share[outl_shr['Sales Unit'].loc[i]] = outl_shr['share'].loc[i]
                
            input_repo['opt_mode']=opt_mode
            input_repo['show_outlay_share'] = show_outlay_share
        else:
            opt_mode = 0
            input_repo['opt_mode']=opt_mode
            show_outlay_share={}
    
        input_repo['channel_client_deal'] = sample
        input_repo['deal_number'] = int(sample.split('|')[-1])
    
        # =============================================================================
        #ck1 = pd.DataFrame({'a':[1,2,3,4],'b':[10,20,30,40]})
        #sum(ck1['a']*ck1['b'])
        
        if 'DF_GRID_RECC_AGG.pickle' in os.listdir():
            print('AGG exists ')
            #opt_feed_fnl.set_index(master_key, inplace=True)
            #opt_feed_fnl.sort_index(inplace=True)
            
            #************************************************
            
            pickle_in = open("DF_GRID_RECC_AGG.pickle","rb")
            DF_GRID_RECC_AGG = pickle.load(pickle_in)
            pickle_in.close()
            
            
            indx = list(DF_GRID_RECC_AGG.index.names)
            DF_GRID_RECC_AGG = DF_GRID_RECC_AGG.reset_index()
                
            DF_GRID_RECC_AGG['year_mon'] = DF_GRID_RECC_AGG['date'].apply(lambda x: int(datetime.datetime.strptime(str(x), "%Y%m%d").strftime("%Y%m")))
            
            #max(DF_GRID_RECC_AGG['year_mon'])
            #max(DF_GRID_RECC_AGG['date'])
            #input_repo['inp_end_dt']
            
            DF_GRID_RECC_AGG['date'] =  DF_GRID_RECC_AGG['date'].apply(lambda x:int(x))
            bs_dt_1     = datetime.datetime.strptime(str(max(DF_GRID_RECC_AGG['date'])), "%Y%m%d")#.strftime("%Y-%m-%d")
            bs_dt_2     = datetime.datetime.strptime(input_repo['inp_end_dt'], "%Y%m%d")
            DF_GRID_RECC_AGG['date'] =  DF_GRID_RECC_AGG['date'].apply(lambda x:str(x))
            
            
            
            year_mon_list = mon_list(bs_dt_1,bs_dt_2,0)
            del bs_dt_1,bs_dt_2
            
            #month_name = year_mon_list[0]
            if len(year_mon_list) >0:
                months_date_repo = []
                for month_name in year_mon_list:
                    if month_name > 201810:
                        months_date_repo.append(date_master_create(month_name))
                    
                comb = pd.concat(months_date_repo) 
                comb = comb[['date', 'Timeband', 'day_name', 'week_num', 'dy_of_week',
                   'week_day_type', 'show_nm', 'stream_type', 'Channel Tags']]
                
                comb['FCT_allocated'] = 0
                comb['obs_count'] = 0
                comb['outlay'] = 0
            
                DF_GRID_RECC_AGG = DF_GRID_RECC_AGG.append(comb)
                p = DF_GRID_RECC_AGG.copy()
                
                pickle_out = open('DF_GRID_RECC_AGG.pickle',"wb")
                pickle.dump(DF_GRID_RECC_AGG, pickle_out)
                pickle_out.close()
    
    
        #--------------------------------------------------------------------------
        #--------------------------------------------------------------------------
        # CREATE DATA FOR CAMPAIGN PERIOD
        #--------------------------------------------------------------------------
        #--------------------------------------------------------------------------
        
        campaign_months  = mon_list(datetime.datetime.strptime(input_repo['inp_strt_dt'], "%Y%m%d"),datetime.datetime.strptime(input_repo['inp_end_dt'], "%Y%m%d"))
        opt_feed_samp = []
        for mon_item in campaign_months:
             opt_feed_samp.append(date_master_create(mon_item))
        opt_feed_fnl = pd.concat(opt_feed_samp)
        #--------------------------------------------------------------------------
        # rename TVR columns 
        opt_feed_fnl['date_join'] = opt_feed_fnl['date'].apply(lambda x : datetime.datetime.strptime(x, "%Y%m%d").strftime("%Y-%m-%d"))
        opt_feed_fnl['show_nm'] = opt_feed_fnl['show_nm'].apply(lambda x : x.upper())
        opt_feed_fnl11 = pd.merge(  opt_feed_fnl
                                 ,  sched_2[['description','date_aired','timeband']]
                                 ,  left_on     = ['date','Timeband']
                                 ,  right_on    = ['date_aired','timeband']
                                 ,  how         = 'left')
    
        
        
        
        
        
        opt_feed_fnl.rename(columns={'TVR_chan': 'TVR_chan_drop','TVR_clnt': 'TVR_clnt_drop'}, inplace=True)
        
        channel_df_dt_agg = pd.read_csv('data/channel_df_dt_agg.csv')
        client_df_dt_agg = pd.read_csv('data/client_df_dt_agg.csv')
        
        channel_df_dt_agg = channel_df_dt_agg[channel_df_dt_agg['SALES_APP_DEAL_ID'] == input_repo['deal_number']]
        
        opt_feed_fnl11 = pd.merge(    opt_feed_fnl
                                ,   channel_df_dt_agg[['description','timeband', 'rate']]
                                ,   left_on     = ['show_nm','Timeband']
                                ,   right_on    = ['description','timeband']
                                ,   how        = 'left')
        
        
    
        chan_tag_check = opt_feed_fnl[(opt_feed_fnl['rate'].isna()) & (opt_feed_fnl['Channel Tags']!= 'DH')][['Sales Unit','rate']]
        
        
        len(opt_feed_fnl['show_nm'].unique())
        len(channel_df_dt_agg['master_program'].unique())
        c1 = channel_df_dt_agg[['timeband','dow','master_program']].drop_duplicates()
        c2 = opt_feed_fnl[['Timeband','day_name','show_nm']].drop_duplicates()
        
        opt_feed_fnl['date'].unique()
        
        
        aa =opt_feed_fnl[opt_feed_fnl['Sales Unit'] == '(Yeh Rishta Kya Kehalata Hai)-(R)-(Mon-Sat)-(18:00-18:30)-(SPSD)']
        #--------------------------------------------------------------------------    
        #drop the days out of the broadcast end date 
        air_dates = pd.read_csv('data/SU_air_strt_end_dt.csv')
        air_dates['broadcast_start_date'] = air_dates['broadcast_start_date'].apply(lambda x: int(datetime.datetime.strptime(x, "%Y-%m-%d").strftime("%Y%m%d")))
        air_dates['broadcast_end_date'] = air_dates['broadcast_end_date'].apply(lambda x: int(datetime.datetime.strptime(x, "%Y-%m-%d").strftime("%Y%m%d")))
    
        
        opt_feed_fnl['date'] = opt_feed_fnl['date'].apply(lambda x : int(x))
        opt_feed_fnl = opt_feed_fnl[(opt_feed_fnl['date']>= int(input_repo['inp_strt_dt'])) & (opt_feed_fnl['date']<= int(input_repo['inp_end_dt']))]
        
        opt_feed_fnl = pd.merge(    opt_feed_fnl
                                ,   air_dates[['name', 'broadcast_start_date', 'broadcast_end_date']]
                                ,   left_on     = 'Sales Unit'
                                ,   right_on    = 'name')
        opt_feed_fnl = opt_feed_fnl.drop(['name'],axis=1)
        opt_feed_fnl = opt_feed_fnl[(opt_feed_fnl['date']>= opt_feed_fnl['broadcast_start_date'])& (opt_feed_fnl['date']<= opt_feed_fnl['broadcast_end_date'])]
        
    #    chk_air = air_dates.groupby(['name']).count().reset_index()
    #    del chk_air
    #    chk_air_2 = air_dates[air_dates['name']=='(Tejomay Ravivar DEVANCHE DEV MAHADEV)-(R)-(Sun)-(10:00-10:30)-(PRSD)']
        #CAMPAIGN_START_DATE_END_DATE
        
    #opt_feed_fnl = date_master_create(201811)#= date_master.copy()
    
    
        # --------- CLIENTS TAG PT-NPT ----------------------
        pt_ref = time_rank_ref('18:30 - 00:00', 'PT')
        npt_ref = time_rank_ref('07:00 - 18:30', 'NPT')
        #pt_ref = time_rank_ref('18:30 - 00:00', 'CPT')
        dh_ref = time_rank_ref('00:00 - 07:00', 'DH')
        tm_ref={}
        tm_ref.update(time_rank_ref('18:30 - 00:00', 'PT'))
        tm_ref.update(time_rank_ref('07:00 - 18:30', 'NPT'))
        tm_ref.update(time_rank_ref('00:00 - 07:00', 'DH'))
        opt_feed_fnl['Client Tags'] = opt_feed_fnl['Timeband'].apply(lambda x: tm_ref[x])
        opt_feed_fnl.rename(columns={'week_day_type': 'chan_wd_type'}, inplace=True)
        
        # --------- CLIENTS TAG WEEKDAY ----------------------
        weekday_client_input = {}
        
        for item in days:
            weekday_client_input.update({item:'WD'})
            
        #[][] -- take the inpiut to modify the weekends 
        weekday_client_input['Sat'] = 'WE'
        weekday_client_input['Sun'] = 'WE'
        
        opt_feed_fnl['clnt_wd_type'] = opt_feed_fnl['day_name'].apply(lambda x:weekday_client_input[x])
        
        # -----------------------------------------------------------------------------
        # ---------- UPDATE THE AVAILABILITY OF THE SLOTS -----------------------------
        # -----------------------------------------------------------------------------
        
        master_key = ['date','Timeband','day_name','week_num','dy_of_week','chan_wd_type','show_nm','stream_type','Channel Tags']
    
        #if aggregated file exists 
        if 'DF_GRID_RECC_AGG.pickle' in os.listdir():
            opt_feed_fnl.set_index(master_key, inplace=True)
            opt_feed_fnl.sort_index(inplace=True)
            
            #************************************************
            
            pickle_in = open("DF_GRID_RECC_AGG.pickle","rb")
            DF_GRID_RECC_AGG = pickle.load(pickle_in)
            pickle_in.close()
            
    #        DF_GRID_RECC_AGG.set_index(master_key, inplace=True)
    #        DF_GRID_RECC_AGG.sort_index(inplace=True)
            
            opt_feed_fnl = pd.merge(    opt_feed_fnl
                                      , DF_GRID_RECC_AGG[['FCT_allocated']]
                                      , left_index    =   True
                                      , right_index   =   True
                                      , how         =   'left'
                                      )
                        
            opt_feed_fnl['FCT_allocated'] = opt_feed_fnl['FCT_allocated'].fillna(0)
            opt_feed_fnl['FCT_available'] = opt_feed_fnl['add_slots'] - opt_feed_fnl['FCT_allocated']
            #************************************************
            
            opt_feed_fnl = opt_feed_fnl.reset_index()
        
            #p = DF_GRID_RECC_AGG.copy()
            #then data exists and do left join 
        else:
            #no existing recommendation
            #either ask for availability file or consider everything is available
            
            #now its considering every FCT is available
            opt_feed_fnl['FCT_allocated'] = 0
            opt_feed_fnl['FCT_available'] = opt_feed_fnl['add_slots'] - opt_feed_fnl['FCT_allocated']
        
        
        master_key.append('Client Tags')
        master_key.append('clnt_wd_type')
        
    
        
        #input_df = opt_feed_fnl.copy()
        channel_tag_occur = opt_feed_fnl.groupby('Channel Tags').agg({'TVR_clnt': ['sum','count']}) #pd.DataFrame(opt_feed_fnl['Channel Tags'].value_counts())
        channel_tag_occur.columns = ['TVR_clnt','chann_count']
        channel_tag_occur['chann_grp_ratio'] = channel_tag_occur['TVR_clnt']/sum(channel_tag_occur['TVR_clnt'])
        channel_tag_occur['chann_cnt_ratio'] = channel_tag_occur['chann_count']/sum(channel_tag_occur['chann_count'])
        
        
        client_tag_occur= opt_feed_fnl.groupby('Client Tags').agg({'TVR_clnt': ['sum','count']})#pd.DataFrame(opt_feed_fnl['Client Tags'].value_counts())
        client_tag_occur.columns = ['TVR_clnt','chann_count']
        client_tag_occur['chann_grp_ratio'] = client_tag_occur['TVR_clnt']/sum(client_tag_occur['TVR_clnt'])
        client_tag_occur['chann_cnt_ratio'] = client_tag_occur['chann_count']/sum(client_tag_occur['chann_count'])
        
        
        chan_wdt_occur=opt_feed_fnl.groupby('chan_wd_type').agg({'TVR_clnt': ['sum','count']})#pd.DataFrame(opt_feed_fnl['chan_wd_type'].value_counts())
        chan_wdt_occur.columns = ['TVR_clnt','chan_wd_type_count']
        chan_wdt_occur['chann_grp_ratio'] = chan_wdt_occur['TVR_clnt']/sum(chan_wdt_occur['TVR_clnt'])
        chan_wdt_occur['chann_cnt_ratio'] = chan_wdt_occur['chan_wd_type_count']/sum(chan_wdt_occur['chan_wd_type_count'])
        
        clnt_wdt_occur=opt_feed_fnl.groupby('clnt_wd_type').agg({'TVR_clnt': ['sum','count']})#pd.DataFrame(opt_feed_fnl['clnt_wd_type'].value_counts())
        clnt_wdt_occur.columns = ['TVR_clnt','clnt_wd_type_count']
        clnt_wdt_occur['chann_grp_ratio'] = clnt_wdt_occur['TVR_clnt']/sum(clnt_wdt_occur['TVR_clnt'])
        clnt_wdt_occur['chann_cnt_ratio'] = clnt_wdt_occur['clnt_wd_type_count']/sum(clnt_wdt_occur['clnt_wd_type_count'])
        
        opt_feed_fnl.set_index(master_key, inplace=True)
        opt_feed_fnl.sort_index(inplace=True)
    
        # -----------------------------------------------------------------------------
        #target_outlay/opt_feed_fnl['Floor Price'].sum()
        #target_GRP/opt_feed_fnl['TVR'].sum()
        # -----------------------------------------------------------------------------
        
        #price_buck = [pr_rn for pr_rn in range(int(date_master['FP Threshold'].min()),int(date_master['Floor Price'].max()),int(100/op))]
        
        # =============================================================================
        #lw_bound = date_master['FP Threshold'].sum()
        # =============================================================================
        
        tm_key_set           = opt_feed_fnl.index.unique()
        chan_key_set         = channel_tag_occur.index.unique()
        clnt_key_set         = client_tag_occur.index.unique()
        chan_wdt_key_set     = chan_wdt_occur.index.unique()
        clnt_wdt_key_set     = clnt_wdt_occur.index.unique()
    
    
    
        def optimization_regular(input_df,threads_input = 10, chan_trig=0, clnt_trig=0 ,show_outlay_share = show_outlay_share ):
            #input_df =  opt_feed_fnl.copy()
            #threads_input = 40
            #prime_increment = 0.2
        
            m = pe.ConcreteModel() 
            
            # Create sets
            m.input_df      = pe.Set(initialize = tm_key_set , dimen = len(master_key))
            m.chan_key_set  = pe.Set(initialize = chan_key_set)
            m.clnt_key_set  = pe.Set(initialize = clnt_key_set)
            m.chan_wdt_key_set   = pe.Set(initialize = chan_wdt_key_set)
            m.clnt_wdt_key_set   = pe.Set(initialize = clnt_wdt_key_set)
            
            #m.price_buck_set = pe.Set(initialize=price_buck)
            
            m.Y     = pe.Var(m.input_df, domain=pe.NonNegativeIntegers,bounds=(0,max_ad_pb))
        #    m.Y_b   = pe.Var(m.input_df, domain=pe.NonNegativeIntegers,bounds=(0,1))
            m.RCP   = pe.Var(m.input_df,within= pe.NonNegativeReals)
     
    #        def obj_rule(m):
    #            return (sum([m.Y[e]*(input_df.loc[e, 'Floor Price'] - m.RCP[e])  for e in tm_key_set])+sum([m.Y[e]*(input_df.loc[e, 'TVR_chan'])  for e in tm_key_set]))
    #        m.OBJ = pe.Objective(rule=obj_rule, sense=pe.minimize)
    
            def obj_rule(m):
                return (sum([m.Y[e]*(input_df.loc[e, 'Floor Price'] - m.RCP[e])  for e in tm_key_set])+sum([m.Y[e]*(input_df.loc[e, 'TVR_chan'])  for e in tm_key_set]))/(sum([m.Y[e]*m.RCP[e]  for e in tm_key_set]))
            m.OBJ = pe.Objective(rule=obj_rule, sense=pe.minimize)
    
            
            
            
            
        #============== IMPACT PUSH - [START] ================================================   
            if opt_mode == 1 :
                
                m.impct_chan    = pe.Set(initialize = list(show_outlay_share.keys()))
                
                def impact_push_show_u(m,j):
                    show_outly = sum([m.Y[e]*m.RCP[e] for e in tm_key_set if j == e[master_key.index('show_nm')]])
                    return show_outly <= target_outlay*(show_outlay_share[j]+0.05)
                    
                m.impact_push_show_cu = pe.Constraint(m.impct_chan, rule = impact_push_show_u)
                
                
                def impact_push_show_l(m,j):
                    show_outly = sum([m.Y[e]*m.RCP[e] for e in tm_key_set if j == e[master_key.index('show_nm')]])
                    return show_outly >= target_outlay*(show_outlay_share[j])
                    
                m.impact_push_show_cl = pe.Constraint(m.impct_chan, rule = impact_push_show_l)
            
        #============== IMPACT PUSH - [END] ================================================   
    
                
        #============== CHANNEL TERMS ================================================   
            if chan_trig == 1:
                def chan_rule_prior_l(m,j):    
                    numer = sum([m.Y[e]*input_df.loc[e, 'TVR_clnt'] for e in tm_key_set if j == e[master_key.index('Channel Tags')]])    
                    denom = sum([m.Y[e]*input_df.loc[e, 'TVR_clnt'] for e in tm_key_set])
                    
                    if (j != 'DH' and j != 'PT'):
                        return  numer >= channel_tag_occur.loc[j,'chann_grp_ratio']*denom*0.3
                    elif j == 'DH':
                        return  numer == 0
                    elif j == 'PT':
                        return  numer >= channel_tag_occur.loc[j,'chann_grp_ratio']*denom*0.3#0.32*denom#*channel_occur.loc[j,'chann_ratio']*(1+prime_increment)
                
                m.chann_prior_ratio_l = pe.Constraint(m.chan_key_set,rule=chan_rule_prior_l)
            
                def chan_rule_wkd_l(m,j):    
                    numer = sum([m.Y[e]*input_df.loc[e, 'TVR_clnt'] for e in tm_key_set if j == e[master_key.index('chan_wd_type')]])    
                    denom = sum([m.Y[e]*input_df.loc[e, 'TVR_clnt'] for e in tm_key_set])
                    
                    if j == 'WD':
                        return  numer >= chan_wdt_occur.loc[j,'chann_grp_ratio']*denom*0.3
                    elif j == 'WE':
                        return  numer >= chan_wdt_occur.loc[j,'chann_grp_ratio']*denom*0.3
                   
                m.chann_wkd_ratio_l = pe.Constraint(m.chan_wdt_key_set,rule=chan_rule_wkd_l)
            
                
        #============== CLIENT TERMS =================================================    
            if clnt_trig == 1:
                def clnt_rule_prior_l(m,j):    
                    numer = sum([m.Y[e]*input_df.loc[e, 'TVR_clnt'] for e in tm_key_set if j == e[master_key.index('Client Tags')]])    
                    denom = sum([m.Y[e]*input_df.loc[e, 'TVR_clnt'] for e in tm_key_set])
                    
                    if (j != 'DH' and j != 'PT'):
                        return  numer >= client_tag_occur.loc[j,'chann_grp_ratio']*denom*0.3
                    elif j == 'DH':
                        return  numer == 0
                    elif j == 'PT':
                        return  numer >= client_tag_occur.loc[j,'chann_grp_ratio']*denom*0.3#0.32*denom#*channel_occur.loc[j,'chann_ratio']*(1+prime_increment)
                
                m.clnt_ratio_prior_l = pe.Constraint(m.clnt_key_set,rule=clnt_rule_prior_l)
            
            
                def clnt_rule_wkd_l(m,j):    
                    numer = sum([m.Y[e]*input_df.loc[e, 'TVR_clnt'] for e in tm_key_set if j == e[master_key.index('clnt_wd_type')]])    
                    denom = sum([m.Y[e]*input_df.loc[e, 'TVR_clnt'] for e in tm_key_set])
                    
                    if (j == 'WD'):
                        return  numer >= clnt_wdt_occur.loc[j,'chann_grp_ratio']*denom*0.5
                    elif j == 'WE':
                        return  numer >= clnt_wdt_occur.loc[j,'chann_grp_ratio']*denom*0.5
                   
                m.clnt_wkd_ratio_l = pe.Constraint(m.clnt_wdt_key_set,rule=clnt_rule_wkd_l)
            
            
            #CPRP Upper bound rule 
    #        def upper_cprp_rule(m):
    #            return sum([m.RCP[e] for e in tm_key_set])/sum([m.Y[e] * input_df.loc[e, 'TVR_clnt'] for e in tm_key_set])>= input_repo['target_cprp']
    #        m.upper_cprp_rl_c = pe.constraint(rule = upper_cprp_rule)
                        
        
            
            # Upper bounds rule
            def upper_bounds_rule_GRP(m):
                return  sum([m.Y[e] * input_df.loc[e, 'TVR_clnt'] for e in tm_key_set]) <= input_repo['target_grp']*1.1
            m.UpperBound_G = pe.Constraint(rule=upper_bounds_rule_GRP)
            
            # Lower bounds rule
            def lower_bounds_rule_GRP(m):
                return sum([m.Y[e]*input_df.loc[e, 'TVR_clnt']for e in tm_key_set]) >=  input_repo['target_grp']*1
            m.LowerBound_G = pe.Constraint(rule=lower_bounds_rule_GRP)
            
            # Upper bounds rule
            def upper_bounds_rule_OTL(m):
                return sum([m.Y[e] * m.RCP[e] for e in tm_key_set]) <= input_repo['target_outlay']*1.2
            m.UpperBound_O = pe.Constraint(rule=upper_bounds_rule_OTL)
            
            def TVR_bounds_rule(m):
                return (sum( [m.Y[e] * input_df.loc[e, 'TVR_clnt'] for e in tm_key_set])-(sum([m.Y[e] * input_df.loc[e, 'TVR_chan'] for e in tm_key_set]))) >= 0.0
            m.TVR_bounds = pe.Constraint(rule=TVR_bounds_rule)
            #
            #def mid2_bounds_rule_OTL(m):
            #    return sum([m.Y[e] * m.RCP[e] for e in tm_key_set]) >= sum([m.Y[e] * input_df.loc[e, 'FP Threshold'] for e in tm_key_set])
            #m.MidBound2_O = pe.Constraint(rule=mid2_bounds_rule_OTL)
            
            
            def prc_cntrl1(m,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11):
                k = (a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11)
                return input_df.loc[k, 'FP Threshold']*m.Y[k] <= m.RCP[k]*m.Y[k]
            m.prcBound1 = pe.Constraint(m.input_df,rule=prc_cntrl1)
            
            def prc_cntrl2(m,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11):
                k = (a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11)
                return input_df.loc[k, 'Floor Price']*m.Y[k] >= m.RCP[k]*m.Y[k]
            m.prcBound2 = pe.Constraint(m.input_df,rule=prc_cntrl2)
            
                    # Upper bounds rule
            def FCT_availability(m,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11):
                k = (a1,a2,a3,a4,a5,a6,a7,a8,a9,a10,a11)
                return  m.Y[k]  <= input_df.loc[k, 'FCT_available']
            m.FCT_availability_m = pe.Constraint(m.input_df,rule=FCT_availability)
            
            
            
            # ------------------------- Solve the model -----------------------------------
            
            strt_tm_cmpt = datetime.datetime.now()
            
            solver = pyomo.opt.SolverFactory('baron')
    #        solver.options['AllowFilterSD'] = 1
    #        solver.options['BoxTol'] = 0.1
    #        solver.options['DeltaTerm'] = 1
    #        solver.options['CutOff'] = 1
            solver.options['MaxTime'] = 1800
            solver.options['threads'] = threads_input
            solver.options['epsr'] = 0.01
            solver.options['DoLocal'] = 0
            
            
            
    #        solver = pyomo.opt.SolverFactory('gurobi')
    #        solver.options['PSDTol'] = 1.1
    #        solver.options['DualReductions'] = 0
    #        solver.options['outlev'] = 1    # tell gurobi to find an iis table for the infeasible model
    #        solver.options['iisfind'] = 1   # tell gurobi to be verbose with output
            
            results = solver.solve(m,keepfiles=True,tee=True)
            end_tm_cmpt = datetime.datetime.now()
            
            print('\n-------------------')
            print(end_tm_cmpt - strt_tm_cmpt)
            print('-------------------\n')
            
            print(results.solver.status)
            print(results.solver.termination_condition)
            
                            
            if (results.solver.status != pyomo.opt.SolverStatus.ok):
                logging.warning('Check solver not ok?')
            if (results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal):    
                logging.warning('Check solver optimality?') 
            
        
            return [m,results.solver.status,results.solver.termination_condition]
        
        
        
    #    def optimization_impactpush(input_df,threads_input = 1, chan_trig=0, clnt_trig=0,show_outlay_share = show_outlay_share):
    #        
    #        #prime_increment = 0.2
    #    
    #        m = pe.ConcreteModel() 
    #        
    #        # Create sets
    #        m.input_df      = pe.Set(initialize = tm_key_set , dimen = len(master_key))
    #        m.chan_key_set  = pe.Set(initialize = chan_key_set)
    #        m.clnt_key_set  = pe.Set(initialize = clnt_key_set)
    #        m.impct_chan    = pe.Set(initialize = list(show_outlay_share.keys()))
    #        
    #        m.wdt_key_set   = pe.Set(initialize = wdt_key_set)
    #        
    #        #m.price_buck_set = pe.Set(initialize=price_buck)
    #        
    #        m.Y     = pe.Var(m.input_df, domain=pe.NonNegativeIntegers,bounds=(0,max_ad_pb))
    #    #    m.Y_b   = pe.Var(m.input_df, domain=pe.NonNegativeIntegers,bounds=(0,1))
    #        m.RCP   = pe.Var(m.input_df,within= pe.NonNegativeReals)
    #        
    #        def obj_rule(m):
    #            return sum([m.Y[e]*(input_df.loc[e, 'Floor Price'] - m.RCP[e])  for e in tm_key_set])+(sum([m.Y[e]*(input_df.loc[e, 'TVR_chan'])  for e in tm_key_set]))  
    #        m.OBJ = pe.Objective(rule=obj_rule, sense=pe.minimize)
    #    
    #
    #    
    #    
    #    #============== CHANNEL TERMS ================================================   
    #        if chan_trig == 1:
    #            def chan_rule_l(m,j):    
    #                numer = sum([m.Y[e] for e in tm_key_set if j == e[master_key.index('Channel Tags')]])    
    #                denom = sum([m.Y[e] for e in tm_key_set])
    #                
    #                if (j != 'DH' and j != 'PT'):
    #                    return  numer >= channel_tag_occur.loc[j,'chann_ratio']*denom*0.5
    #                elif j == 'DH':
    #                    return  numer == 0
    #                elif j == 'PT':
    #                    return  numer >= 0.32*denom#*channel_occur.loc[j,'chann_ratio']*(1+prime_increment)
    #            
    #            m.chann_ratio_l = pe.Constraint(m.chan_key_set,rule=chan_rule_l)
    #        
    #    #============== CLIENT TERMS =================================================    
    #        if clnt_trig == 1:
    #            def clnt_rule_l(m,j):    
    #                numer = sum([m.Y[e] for e in tm_key_set if j == e[master_key.index('Client Tags')]])    
    #                denom = sum([m.Y[e] for e in tm_key_set])
    #                
    #                if (j != 'DH' and j != 'PT'):
    #                    return  numer >= client_tag_occur.loc[j,'chann_ratio']*denom*0.5
    #                elif j == 'DH':
    #                    return  numer == 0
    #                elif j == 'PT':
    #                    return  numer >= 0.32*denom#*channel_occur.loc[j,'chann_ratio']*(1+prime_increment)
    #            
    #            m.clnt_ratio_l = pe.Constraint(m.clnt_key_set,rule=clnt_rule_l)
    #        
    #        
    #        
    #        def impact_push_show_u(m,j):
    #            show_outly = sum([m.Y[e]*m.RCP[e] for e in tm_key_set if j == e[master_key.index('show_nm')]])
    #            return show_outly <= target_outlay*(show_outlay_share[j]+0.05)
    #            
    #        m.impact_push_show_cu = pe.Constraint(m.impct_chan, rule = impact_push_show_u)
    #        
    #        
    #        def impact_push_show_l(m,j):
    #            show_outly = sum([m.Y[e]*m.RCP[e] for e in tm_key_set if j == e[master_key.index('show_nm')]])
    #            return show_outly >= target_outlay*(show_outlay_share[j])
    #            
    #        m.impact_push_show_cl = pe.Constraint(m.impct_chan, rule = impact_push_show_l)
    #        
    #        
    #        
    #        
    #        # Upper bounds rule
    #        def upper_bounds_rule_GRP(m):
    #            return  sum([m.Y[e] * input_df.loc[e, 'TVR_clnt'] for e in tm_key_set]) <= input_repo['target_grp']*1.1
    #        m.UpperBound_G = pe.Constraint(rule=upper_bounds_rule_GRP)
    #        
    #        # Lower bounds rule
    #        def lower_bounds_rule_GRP(m):
    #            return sum([m.Y[e]*input_df.loc[e, 'TVR_clnt']for e in tm_key_set]) >=  input_repo['target_grp']*1
    #        m.LowerBound_G = pe.Constraint(rule=lower_bounds_rule_GRP)
    #        
    #        # Upper bounds rule
    #        def upper_bounds_rule_OTL(m):
    #            return sum([m.Y[e] * m.RCP[e] for e in tm_key_set]) <= input_repo['target_outlay']*1
    #        m.UpperBound_O = pe.Constraint(rule=upper_bounds_rule_OTL)
    #        
    #        def TVR_bounds_rule(m):
    #            return (sum( [m.Y[e] * input_df.loc[e, 'TVR_clnt'] for e in tm_key_set])-(sum([m.Y[e] * input_df.loc[e, 'TVR_chan'] for e in tm_key_set]))) >= 0.0
    #        m.TVR_bounds = pe.Constraint(rule=TVR_bounds_rule)
    #    
    #        #
    #        #def mid2_bounds_rule_OTL(m):
    #        #    return sum([m.Y[e] * m.RCP[e] for e in tm_key_set]) >= sum([m.Y[e] * input_df.loc[e, 'FP Threshold'] for e in tm_key_set])
    #        #m.MidBound2_O = pe.Constraint(rule=mid2_bounds_rule_OTL)
    #        
    #        
    #        def prc_cntrl1(m,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10):
    #            k = (a1,a2,a3,a4,a5,a6,a7,a8,a9,a10)
    #            return input_df.loc[k, 'FP Threshold']*m.Y[k] <= m.RCP[k]*m.Y[k]
    #        m.prcBound1 = pe.Constraint(m.input_df,rule=prc_cntrl1)
    #        
    #        def prc_cntrl2(m,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10):
    #            k = (a1,a2,a3,a4,a5,a6,a7,a8,a9,a10)
    #            return input_df.loc[k, 'Floor Price']*m.Y[k] >= m.RCP[k]*m.Y[k]
    #        m.prcBound2 = pe.Constraint(m.input_df,rule=prc_cntrl2)
    #        
            
            # ------------------------- Solve the model -----------------------------------
    #        
    #        strt_tm_cmpt = datetime.datetime.now()
    #        
    #        solver = pyomo.opt.SolverFactory('baron')
    #        solver.options['AllowFilterSD'] = 1
    #        solver.options['BoxTol'] = 0.1
    #        solver.options['DeltaTerm'] = 1
    #        #solver.options['CutOff'] = 1
    #        solver.options['MaxTime'] = 1800
    #        solver.options['threads'] = threads_input
    #        solver.options['epsr'] = 0.01
    #        
    #        
    #        
    #        #solver = pyomo.opt.SolverFactory('gurobi')
    #        #solver.options['PSDTol'] = 1
    #        
    #        results = solver.solve(m,keepfiles=True,tee=True)
    #        end_tm_cmpt = datetime.datetime.now()
    #        
    #        print('\n-------------------')
    #        print(end_tm_cmpt - strt_tm_cmpt)
    #        print('-------------------\n')
    #        
    #        print(results.solver.status)
    #        print(results.solver.termination_condition)
    #        
    #                        
    #        if (results.solver.status != pyomo.opt.SolverStatus.ok):
    #            logging.warning('Check solver not ok?')
    #        if (results.solver.termination_condition != pyomo.opt.TerminationCondition.optimal):    
    #            logging.warning('Check solver optimality?') 
    #        
    #    
    #        return [m,results.solver.status,results.solver.termination_condition]
    #    
    #    
        
    
    
    
        #==============================================================================
        #       SELECT OPTIMIZATION MODE
        #==============================================================================
    #    if opt_mode == 0 :
    #        test_m = optimization_regular(opt_feed_fnl,40,1,1)
    #    elif opt_mode == 1 :
    #        test_m = optimization_impactpush(opt_feed_fnl,40,0,0,show_outlay_share)
    #        
        test_m = optimization_regular(opt_feed_fnl,40,1,1,show_outlay_share)
        m = test_m[0]
        
        if str(test_m[2]) != 'infeasible':
    
            #show_outlay_share = {'Amazon Abhiyaan': 0.15,'Kulfi Kumar Baajwala':0.15}
            #test_m = optimization_impactpush(opt_feed_fnl,0,0,show_outlay_share)
            #m = test_m[0]
            
            #del test_m
            
            #cc = opt_feed_fnl.reset_index()
            #cc.groupby(['show_nm'])[['Floor Price']].sum()
            #
            #cc1 = cc[cc['show_nm']=='Dance Plus']
            
            
            #def chan_rule_u(m,j):    
            #    return sum([m.Y[e] for e in tm_key_set if j == e[3]])/sum([m.Y[e2] for e2 in tm_key_set])channel_occur.loc[j,'chann_ratio'] )
            #m.chann_ratio_u = pe.Constraint(m.chan_key_set,rule=chan_rule_u)
               
            dec_var = [str(v) for v in m.component_objects(Var,active=True)]
            print(dec_var)
                
            for v in dec_var:
                #if str(v) == 'Y':
                varobject = getattr(m, str(v))
                print(v)
                print(varobject)
                    
                opt_out = {}    
                key_id = list(tm_key_set.names)
                
                for id_num in range(0,len(key_id)):
                    globals()['key_list_{}'.format(id_num)] =[]
                value_list = []
                
                for index in varobject:
                    for id_num in range(0,len(key_id)):
                        globals()['key_list_{}'.format(id_num)].append(index[id_num])
                        
                    value_list.append(varobject[index].value)
                
                for id_num in range(0,len(key_id)):            
                    opt_out[key_id[id_num]] = globals()['key_list_{}'.format(id_num)]
            
                opt_out['value'] = value_list
                
                globals()['opt_out_df_'+v] = pd.DataFrame(opt_out)
                globals()['opt_out_df_'+v].set_index(master_key, inplace=True)
                globals()['opt_out_df_'+v].sort_index(inplace=True)
            
            #==============================================================================
            #
            #    OPTIMIZATION COMPLETE THE CORRESPONIND DECISION VARIABLE COMPUTATION
            #    
            #==============================================================================
              
            globals()['DF_GRID_RECC_CLIENT_'+client_key] = pd.merge(     opt_feed_fnl#date_master
                                       ,    opt_out_df_Y
                                       ,    right_index=True
                                       ,    left_index = True
                                       
                                      )
            globals()['DF_GRID_RECC_CLIENT_'+client_key].rename(columns={'value':'bucket_select'}, inplace=True)
            
            globals()['DF_GRID_RECC_CLIENT_'+client_key] = pd.merge(     globals()['DF_GRID_RECC_CLIENT_'+client_key]
                                       ,    opt_out_df_RCP
                                       ,    left_index = True
                                       ,    right_index=True
                                      )
            globals()['DF_GRID_RECC_CLIENT_'+client_key].rename(columns={'value':'recom_prc'}, inplace=True)
            
            #------------------------------------------------------------------------------
            #   JOIN THE OPTIMIZATION RESULT
            #------------------------------------------------------------------------------
            
            
            globals()['DF_GRID_RECC_CLIENT_'+client_key]['bucket_select']=globals()['DF_GRID_RECC_CLIENT_'+client_key]['bucket_select'].apply(lambda x : round(x))
            
            globals()['DF_GRID_RECC_CLIENT_'+client_key]['recom_prc']=globals()['DF_GRID_RECC_CLIENT_'+client_key]['recom_prc'].apply(lambda x : round(x))
            globals()['DF_GRID_RECC_CLIENT_'+client_key] = globals()['DF_GRID_RECC_CLIENT_'+client_key][globals()['DF_GRID_RECC_CLIENT_'+client_key]['bucket_select']>0]
            
            globals()['DF_GRID_RECC_CLIENT_'+client_key] = globals()['DF_GRID_RECC_CLIENT_'+client_key].reset_index()
            #globals()['DF_GRID_RECC_'+client_key] = globals()['DF_GRID_RECC_'+client_key][globals()['DF_GRID_RECC_'+client_key]['bucket_select']>0]
            globals()['DF_GRID_RECC_CLIENT_'+client_key]['client_name'] = client_lookup[client_key]
            globals()['DF_GRID_RECC_CLIENT_'+client_key]['outlay'] = globals()['DF_GRID_RECC_CLIENT_'+client_key]['bucket_select']*globals()['DF_GRID_RECC_CLIENT_'+client_key]['recom_prc']
            
            p = globals()['DF_GRID_RECC_CLIENT_'+client_key].copy()
            p = p.reset_index()
            
            print('\n------------------------------------------------------------------------------')
            print('   POST OPTIMIZATION : RESULT COLLATE ')
            print('------------------------------------------------------------------------------')
            print('Channel GRP \t: \t{}'.format((p['TVR_chan']*p['bucket_select']).sum()))
            print('Client GRP \t: \t{}'.format((p['TVR_clnt']*p['bucket_select']).sum()))
            
            
            
            print('\n')
            print(p['clnt_wd_type'].value_counts())
            print('\n')
            print(p['Channel Tags'].value_counts())
            print('\n')
            print(p.groupby(['Channel Tags'])[['bucket_select']].sum())
            print('\n')
            print(p.groupby(['Client Tags'])[['bucket_select']].sum())
            print('\n')
            print(p.groupby(['show_nm','bucket_select'])[['recom_prc']].sum())
            print('\n')
            print(p['show_nm'].value_counts())
            
            p['disc_max'] = p['Floor Price'] - p['recom_prc']
            p['disc_min'] = p['recom_prc'] - p['FP Threshold']
            
            def disc_chk(a,b):
                if a!=0 and b!=0:
                    return 1
                else: 
                    return 0
            disc_chk(0,1)
                
            p['disc_chk'] = p.apply(lambda x: disc_chk(x['disc_max'],x['disc_min']),axis=1)
            
            floor_outlay = (p['Floor Price']*p['bucket_select']).sum()
            print('\n')
            print('Floor Outlay \t\t: \t{}'.format(floor_outlay))
            outlay_thresh = (p['FP Threshold']*p['bucket_select']).sum()
            print('Outlay Thresh \t\t: \t{}'.format(outlay_thresh))
            recom_outlay = (p['recom_prc']*p['bucket_select']).sum()
            print('Recommended Outlay \t: \t{}'.format(recom_outlay))
            discount = 1-(recom_outlay/floor_outlay)
            print('Discount \t\t: \t{}'.format(discount))
            print('\n')
            print(p['disc_chk'].value_counts())
            
            
            #['CL_GRP'] = p['bucket_select']*p['TVR_clnt']
            #recc_cprp     =   sum(p['outlay']*p['CL_GRP'])/sum(p['CL_GRP'])
            
            
            #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            #xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            
            print('\n')
            print('DF_GRID_RECC_'+client_key+'\t is recommended grid for client')
            print('DF_GRID_RECC_AGG \t is aggregated inventory sold/recommended - SU level data')
            print('DF_GRID_RECC_LN_DTL \t is line detail of inventory sold/recommended - SU-Client level data')
            print('\n')
            print('------------------------------------------------------------------------------')
            
            pickle_out = open('DF_GRID_RECC_CLIENT_'+client_key+'.pickle',"wb")
            pickle.dump(globals()['DF_GRID_RECC_CLIENT_'+client_key], pickle_out)
            pickle_out.close()
            
            #------------------------------------------------------------------------------
            # create or uodate LN_DTL
            globals()['DF_GRID_RECC_CLIENT_'+client_key] = globals()['DF_GRID_RECC_CLIENT_'+client_key].drop([
                                                        'Client Tags'
                                                    ,   'day_nm'
                                                    ,   'Sales Unit'
                                                    ,   'Floor Price'
                                                    ,   'FP Threshold'
                                                    ,   'days_numb'
                                                    ,   'show_duration_mins'
                                                    ,   'sub_buckets_count'
                                                    ,   'add_slots'
                                                    ,   'trig_ind'
                                                    ,   'count'
                                                    ,   'FCT_allocated'
                                                    ,   'FCT_available'
                                                    ,   'buck_countr'
                                                                                ],axis=1)
             
            globals()['DF_GRID_RECC_CLIENT_'+client_key].columns
                    
            if 'DF_GRID_RECC_LN_DTL.pickle' in os.listdir():
                #read and append
                pickle_in = open("DF_GRID_RECC_LN_DTL.pickle","rb")
                DF_GRID_RECC_LN_DTL = pickle.load(pickle_in)
                pickle_in.close()
                
                DF_GRID_RECC_LN_DTL = DF_GRID_RECC_LN_DTL.reset_index()
                DF_GRID_RECC_LN_DTL = DF_GRID_RECC_LN_DTL.append(globals()['DF_GRID_RECC_CLIENT_'+client_key])
                
            else:
                #create 
                DF_GRID_RECC_LN_DTL = globals()['DF_GRID_RECC_CLIENT_'+client_key].copy()
            
            #------------------------------------------------------------------------------
            #   Compute Aggregated table
            import numpy as np
            
            DF_GRID_RECC_AGG = DF_GRID_RECC_LN_DTL.groupby(master_key[:-1]).agg({
                                                        'bucket_select': [np.sum,np.size]
                                                   ,    'outlay': np.sum
                                                   })
            
            DF_GRID_RECC_AGG.columns = ['FCT_allocated','obs_count','outlay']
            DF_GRID_RECC_AGG.sort_index(inplace=True)
            
            sort_data = master_key[:-1].copy()
            sort_data.append('client_name')
            print(sort_data)
            DF_GRID_RECC_LN_DTL = DF_GRID_RECC_LN_DTL.sort_values(sort_data)
            DF_GRID_RECC_LN_DTL.set_index(sort_data, inplace=True)
            DF_GRID_RECC_LN_DTL.sort_index(inplace=True)
            #DF_GRID_RECC_LN_DTL = DF_GRID_RECC_LN_DTL.sort_values(['client_name'])
            p = DF_GRID_RECC_LN_DTL.copy()
            
            pickle_out = open('DF_GRID_RECC_LN_DTL.pickle',"wb")
            pickle.dump(DF_GRID_RECC_LN_DTL, pickle_out)
            pickle_out.close()
            
            
            pickle_out = open('DF_GRID_RECC_AGG.pickle',"wb")
            pickle.dump(DF_GRID_RECC_AGG, pickle_out)
            pickle_out.close()
        

channel_df_dt_agg = pd.read_csv('data/channel_df_dt_agg.csv')
final_deal = channel_df_dt_agg['SALES_APP_DEAL_ID'].unique().tolist()
del channel_df_dt_agg


for sample in sls_deal_key_lst :
    client_list = []
    for item in  os.listdir():
        if 'DF_GRID_RECC_CLIENT_' in item:
            client_list.append(str(item.split('_')[-1].split('.')[0]))
        
    #sample = 'Star_Plus|Abbott_Healthcare|2025'
    if sample.split('|')[-1] not in client_list and int(sample.split('|')[-1]) not in final_deal:
        try:
            main_module(sample)
        except:
            print('--------- ERROR ------------')
            pass




#opt_end_ver_sv()
#
#date_master_out2['bucket_select'].unique()
#
#date_master_out2.groupby(['show_nm'])[['Floor Price']].sum()
#date_master_out2.groupby(['show_nm'])[['TVR']].sum()
#date_master_out2.groupby(['show_nm'])[['bucket_select']].sum()
#date_master_out2.groupby(['show_nm'])[['recom_prc']].sum()
#
#date_master_out2['Floor Price'].value_counts()
#
#date_master = date_master.reset_index()
#
#date_master['week_day_type'].value_counts()
#date_master['Channel Tags'].value_counts()
#
#channel_occur
#wdt_occur
#
## =============================================================================
#
#
#import pickle
#pickle_in = open("log_dir_7/date_master_out2.pickle","rb")
#date_master_out3 = pickle.load(pickle_in)
#
#
#date_master_out3['rec_GRP'] = date_master_out3['TVR']*date_master_out3['bucket_select'] 
#date_master_out3['actl_outlay'] = date_master_out3['Floor Price']*date_master_out3['bucket_select']*100 
#date_master_out3['rec_outlay'] = date_master_out3['recom_prc']*date_master_out3['bucket_select']*100 
#
#opt_explore_1 = date_master_out3.groupby(['show_nm', 'stream_type','day_name', 'Channel Tags', 'week_day_type','Timeband'])[['bucket_select','rec_GRP','actl_outlay','rec_outlay']].sum()
#opt_explore_1 =opt_explore_1.reset_index()
##opt_explore_1['rec_outlay'].sum()
#opt_explore_1.to_csv('opt_explore_1.csv')
##opt_explore_1['strt_tm'] = opt_explore_1['Timeband'].apply(lambda x:datetime.datetime.strptime(x.split(' - ')[0],'%H:%M'))
##opt_explore_1['end_tm'] = opt_explore_1['Timeband'].apply(lambda x:datetime.datetime.strptime(x.split(' - ')[1],'%H:%M'))
#
#def f(x):
#     return pd.Series(dict(A = "{%s}" % ', '.join(x['Timeband']), 
#                        B = "{%s}" % ', '.join(x['bucket_select'])
#                        ))
##                        C = "{%s}" % ', '.join(x['C'])))
# 
#opt_explore_2_1 = pd.DataFrame(opt_explore_1.groupby(['show_nm', 'stream_type','day_name', 'Channel Tags', 'week_day_type'])['bucket_select'].apply(list))
#opt_explore_2_2 = pd.DataFrame(opt_explore_1.groupby(['show_nm', 'stream_type','day_name', 'Channel Tags', 'week_day_type'])['Timeband'].apply(list))
#opt_explore_2 = pd.merge(     opt_explore_2_1
#                           ,    opt_explore_2_2
#                           ,    left_index = True
#                           ,    right_index=True
#                          )



#number of hours for all shows

