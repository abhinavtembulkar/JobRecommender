import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import warnings; warnings.simplefilter('ignore')

apps = pd.read_csv('apps.tsv', delimiter='\t',encoding='utf-8')
print ('shape of apps data - {}'.format(apps.shape))
# apps.head()

jobs = pd.read_csv('jobs.tsv', delimiter='\t',encoding='utf-8', error_bad_lines=False,nrows=40000)
print ('shape of jobs data - {}'.format(jobs.shape))
# jobs.head()

users = pd.read_csv('users.tsv' ,delimiter='\t',encoding='utf-8',nrows=10000)
print ('shape of users data - {}'.format(users.shape))
# users.head()

apps_training = apps[apps['Split']=='Train']
users_training = users[users['Split']=='Train']
user_training_US = users_training[users_training['Country']=='US']

user_training_US['City'] = user_training_US['City'].fillna('')
user_training_US['DegreeType'] = user_training_US['DegreeType'].fillna('Not Applicable')
user_training_US['Major'] = user_training_US['Major'].fillna('Not Applicable')
user_training_US['GraduationDate'] = user_training_US['GraduationDate'].fillna('Not Applicable')
user_training_US['WorkHistoryCount'] = user_training_US['WorkHistoryCount'].fillna('0').astype(str)
user_training_US['TotalYearsExperience'] = user_training_US['TotalYearsExperience'].fillna('0').astype(str)
user_training_US['CurrentlyEmployed'] = user_training_US['DegreeType'].fillna('Not Applicable')
user_training_US['ManagedHowMany'] = user_training_US['ManagedHowMany'].fillna('0').astype(str)

# cosine_sim
# userid
# indices

def get_recommendations_userwise(userid):
    idx = indices[userid]
    #print (idx)
    global cosine_sim
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    user_indices = [i[0] for i in sim_scores]
    return user_indices[0:11]

def get_job_id(usrid_list):
    jobs_userwise = apps_training['UserID'].isin(usrid_list) #
    df1 = pd.DataFrame(data = apps_training[jobs_userwise], columns=['JobID'])
    joblist = df1['JobID'].tolist()
    Job_list = jobs['JobID'].isin(joblist) #[1083186, 516837, 507614, 754917, 686406, 1058896, 335132])
    df_temp = pd.DataFrame(data = jobs[Job_list], columns=['JobID','Title','Description','City','State'])
    return df_temp

print('DONE')

while(1):

    command = input()
    print('PYTHON',command)

    if(command == 'CHECK'):
        print(user_training_US.shape)
        print(user_training_US.tail())
        print('DONE')
    elif(command == 'DATA'):
        import json
        command = input()
        print('PYTHON',command)
        command = json.loads(command)
        # command = {"City":"Washington","DegreeType":"HighSchool","Major":"Management","GraduationDate":"2004-08-04","WorkHistoryCount":"1","TotalYearsExperience":"4","CurrentlyEmployed":"Masters","ManagedHowMany":"4"}
        user_training_US = user_training_US.append(command,ignore_index=True)
        new_detail = user_training_US
        new_applicant = new_detail['City']+new_detail['DegreeType']+new_detail['Major']+new_detail['GraduationDate']+new_detail['WorkHistoryCount']+new_detail['TotalYearsExperience']+new_detail['CurrentlyEmployed']+new_detail['ManagedHowMany']
        tf = TfidfVectorizer(analyzer='word',ngram_range=(1, 3),min_df=0, stop_words='english')
        tfidf_matrix = tf.fit_transform(new_applicant)
        global cosine_sim
        print('LOADING')
        cosine_sim = linear_kernel(tfidf_matrix,tfidf_matrix)
        user_training_US = user_training_US.reset_index()
        print('ENDS')
        print('DONE')

    elif(command == 'PROCESS'):
        global userid, indices
        userid = user_training_US['UserID']
        indices = pd.Series(user_training_US.index, index=user_training_US['UserID'])

        # print(user_training_US.iloc[-1,:])
        inds = int(user_training_US.iloc[-1,0])
        inds = userid[inds]

        # Maps index to userid
        # print(userid)
        # maps UserID to index
        # print(indices)
        # inds is UserID

        # print (f"-----Top 10 Similar users with userID:{inds}------")
        answ = get_recommendations_userwise(inds)
        # print (userid[answ].tolist(),'<br>')
        
        suggestjobs = get_job_id(userid[answ])
        print('<br>','-------------Top jobs related to your profile-------------','<br>')
        print('<br>',list(suggestjobs.columns),'<hr>')
        # result = suggestjobs.to_json(orient="values")
        # print(result)
        
        print('<ol>')
        for index,entry in suggestjobs.iterrows():
            print('<li>',entry['JobID'],entry['Title'],entry['City'],entry['State'],'<br>')
            print('<div style="height:150px;width:480px;border:1px solid #ccc;font:16px/26px Georgia, Garamond, Serif;overflow:auto;">',entry['Description'],'</div></li>')
        print('</ol>')
        print('DONE')
        # print(suggestjobs)

    elif(command=='EXIT'):
        break


