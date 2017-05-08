import urllib2
import base64
import json
import time 


# make this DRY

# varibales to be reused: API key + : b64 encoded endpoint url 'https://harvest.greenhouse.io/v1/' then append based on operation

# functions to be reused: GET request with different URLs for list of users, candidates, jobs => return list of id's + name in a tuple?
# also needs to be able to paginate and append more tuples? Use recursion to go to next header['link']

# DELETE request that loopes over a list of id's 

# POST reqeust to create jobs, candidates, applications? 

api = 'Basic ' + base64.b64encode(raw_input('harvest api key> ').strip() + ':')


burl = 'https://harvest.greenhouse.io/v1/'

# get a list of objects, present them to user, return users selection
def get_list(url, query=''):

    # append specific objects to retrive to end of base url 
    url = url + query
    req = urllib2.Request(url)
    req.add_header('Authorization', api)

    try:
        handle = urllib2.urlopen(req)
        #  save value of headers to be used to get next link and check x-ratelimit-remaining
        header = dict(handle.info())

    except urllib2.HTTPError as e:
        print e.read()
    except urllib2.URLError as e:
        print e.read()
    
    # check for throttling and wait 10s if true
    if int(header['x-ratelimit-remaining']) < 1:
        time.sleep(10)
    
    handle = json.load(handle)
    
    # parse out next page url if it exists
    s = header['link'].split(',')
    if len(s) > 1:
        # isolate index 0 to get new list of url and rel value
        s = s[0].split(';')
            # check for index 1 to see if value == rel="next"
        if s[1].strip() == 'rel="next"':
            nex_url = s[0].strip('<>')
            
        else:
            nex_url = False

    else:
        nex_url = False
            
    
    return handle, nex_url 

# add an order to reults from get_list and ask to search next page if available

def next_page(r_ls, page):

    for each in r_ls:
            #problem is this only works for candidates need to make this loop a function? 
            # need to add a number for selection, do we make it a key on existing dict of candidate? Why not? Call it ord 
        each['ord'] = r_ls.index(each)
        
        print str(each['ord']) + ' ' + each['first_name'] + ' ' + each['last_name']

    while page:
        
        # ask if they want to see next page
        ask_u = raw_input('next page? Y/n> ').strip().lower()

        if ask_u == 'y':
            
            add, page = get_list(page)    
            
            r_ls.extend(add)    
            
            for each in r_ls[-len(add):]:
                
                each['ord'] = r_ls.index(each)

                print str(each['ord']) + ' ' + each['first_name'] + ' ' + each['last_name']
        
        else:

            break 

    try:
        ask_from_manip = int(raw_input('select candidate from start #: ').strip())
    except ValueError:
        ask_from_manip = int(raw_input('numbers only please: ').strip())


    try:
        ask_to_manip = int(raw_input('to end #: ').strip()) 
    except ValueError:
        ask_to_manip = int(raw_input('numbers only please: ').strip()) 

    if ask_to_manip == ask_from_manip:
        to_manip = r_ls[ask_from_manip]

    else:

        to_manip = r_ls[ask_from_manip:(ask_to_manip + 1)]

    for each in to_manip:

        print str(each['ord']) + ' ' + each['first_name'] + ' ' + each['last_name']
    
    # returns a list of candidate objects from which you can grab any key's value
    return to_manip

# page through results with key 'name' and return 1 user choice not range
def next_page_one(r_ls, page):

    for each in r_ls:
        # need to add a number for selection, do we make it a key on existing dict of candidate? Why not? Call it ord 
        each['ord'] = r_ls.index(each)
        
        # check to see r_ls has a status key
        if 'status' in each:
            # only show open, THIS WILL CONFLICT WITH STATUS OF APPLICATIONS
            if each['status'] == 'open':
                print str(each['ord']) + ' ' + each['name']
            else:
                continue 

        else:

            print str(each['ord']) + ' ' + each['name'] 

    while page:
        
        # ask if they want to see next page
        ask_u = raw_input('next page? Y/n> ').strip().lower()

        if ask_u == 'y':
            # make request for next page
            add, page = get_list(page)    
            # add results to exising list
            r_ls.extend(add)    
            
            for each in r_ls[-len(add):]:
                
                each['ord'] = r_ls.index(each)

                if 'status' in each:
                    if each['status'] == 'open':
                        print str(each['ord']) + ' ' + each['name']

                else:

                    print str(each['ord']) + ' ' + each['name']
        
        else:

            break 
    
    # collect user input for 1 choice
    try:
        ask_from_manip = int(raw_input('make selection by #: ').strip())
    except ValueError:
        ask_from_manip = int(raw_input('numbers only please: ').strip())

    # collect single object to return 
    to_manip = r_ls[ask_from_manip]

    print 'selection: ' + to_manip['name'] + ' ' + str(to_manip['id'])

    return to_manip


#print main menu

def main_menu():

    options = [('candidates', candidates_menu), ('applications', applications_menu),('jobs', jobs_menu), ('users', users_menu), ('offices', offices_menu), 
    ('departments', departments_menu), ('tracking link', tracking_link)]

    for each in options:
        # show each option with a number to assign to it
        print str(options.index(each)) + ': ' + each[0]

    try:
        # test answer for existence in list of choices 
        user_choice = int(raw_input('select category by number> ').strip())

        if (user_choice > len(options) - 1) or user_choice < 0:
            
            user_choice = int(raw_input('# not in list> ').strip())

    except ValueError:
        # prompt for a number in case of a non covertable response
        user_choice = int(raw_input('number in menu only> '))

    # return string with the name of the option, need to create sub menus for each of these options an possibly call that instead of return something
    return options[user_choice][1]()

# candidates menu

def candidates_menu():
    
    # function to add candidates in bulk
    def add_can_bulk():
        
        # make initial call to get list of users
        u_ls, n_page = get_list(burl, 'users')
        
        # prompt selection of users to send on-behalf-of
        obo_obj = next_page_one(u_ls, n_page)

        # use for special On-Behalf-Of header
        obo_id_str = str(obo_obj['id'])
        
        # make call for list of open jobs to add to 
        j_ls, ne_page = get_list(burl, 'jobs')

        # extra page of jobs if neccessary and return selection for id used in application

        job_obj = next_page_one(j_ls, ne_page)

        # ask for number of candidates to add
        quant = int(raw_input('how many candidates to add?> ').strip())

        can_key = ['first_name', 'last_name', 'email_first_part', 'email_at_domain']

        data_w = {}

        # create series of prompts to ask for inputs into application object
        for each in can_key:

            data_w[each] = raw_input(each + ': ').strip()

        
        for cntr in range(quant):

            data_p = {'first_name': data_w['first_name'], 'last_name': data_w['last_name'] + str(cntr), 'email_addresses': [{'value': data_w['email_first_part'] + str(cntr) + data_w['email_at_domain'], 'type': 'personal'}], 'applications': [{'job_id': job_obj['id']}]}    
        
        # loop through range and POST a candidate with itterations on name and emails that are passed in the data object.
            dataj = json.dumps(data_p)

            can_p_req = urllib2.Request(burl+'candidates', dataj)

            can_p_req.add_header('Authorization', api)

            can_p_req.add_header('On-Behalf-Of', obo_id_str)

            try:
                can_handle = urllib2.urlopen(can_p_req)

                # check response headers to check value of X-RateLimit-Remaining 
                x_rate_hdr = dict(can_handle.info())    
                if int(x_rate_hdr['x-ratelimit-remaining']) == 0:
            
                    # if 0 time.sleep(10)
                    time.sleep(10)
        
                else:
                    continue



            except (urllib2.HTTPError, urllib2.URLError) as e:
                print e.info()
                print e.read()
                print e.reason()

        print 'Done'
    
    # delete candidates by range
    def del_can():
        
        raw_input('First select SiteAdmin to perform action [Enter to continue]')
        # make initial call to get list of users
        u_ls, n_page = get_list(burl, 'users')

        # prompt selection of users to send on-behalf-of
        obo_obj = next_page_one(u_ls, n_page)

        obo_id_str = str(obo_obj['id'])

        # get list of candidates
        d_ls, n_page = get_list(burl, 'candidates')

        # collect range of canididates to delete
        ls_can_obj = next_page(d_ls, n_page)


        for each in ls_can_obj:

            del_can_req = urllib2.Request(burl + 'candidates/' + str(each['id']))

            del_can_req.add_header('Authorization', api)

            del_can_req.add_header('On-Behalf-Of', obo_id_str)

            # add specific method to requests
            del_can_req.get_method = lambda: 'DELETE'

            try:
                dcan_handle = urllib2.urlopen(del_can_req)

                x_rate_hdr = dict(dcan_handle.info())    
                
                if int(x_rate_hdr['x-ratelimit-remaining']) == 0:
            
                    # if 0 time.sleep(10)
                    time.sleep(10)
        
                else:
                    continue

            except (urllib2.HTTPError, urllib2.URLError) as e:
                print e.info()
                print e.read()
            
        
        print 'Message: ' + str(len(ls_can_obj)) + ' Deleted'

    #another list of tuples with name of function
    c_options = [('add bulk', add_can_bulk), ('delete range', del_can)]

    for each in c_options:
        # show each option with a number to assign to it
        print str(c_options.index(each)) + ': ' + each[0]

    try:
        # test answer for existence in list of choices 
        user_choice = int(raw_input('select category by number> ').strip())

        if (user_choice > len(c_options) - 1) or user_choice < 0:
            
            user_choice = int(raw_input('# not in list> ').strip())

    except ValueError:
        # prompt for a number in case of a non covertable response
        user_choice = int(raw_input('number in menu only> '))

    # return string with the name of the option, need to create sub menus for each of these options an possibly call that instead of return something
    return c_options[user_choice][1]()

    # TEST to see if next_page works
    #rc_ls, page = get_list(burl, 'candidates')
    #next_page(rc_ls, page)

def applications_menu():

    # grab applications by job and advance them one stage
    # this requires current job_stage id don't think this is on the application object? 
    print 'Under Construction'       

def jobs_menu():
    
    # THIS SHOULD BE AN APPLICATIONS MENU
    # need user to advance on behalf of
    # get_list next_page_one of jobs
    # get list of applications on a job using ?job_id=str(ls_job_obj['id'])
    # get_list next_page_one stages on that job using /jobs/job_id/stages 
    # somehow present range of candidates who have applications on job for user to select, use ?job_id= with /candidates
    # grab range of those candidates and from each use grab application_id but wait that will not work if 2, have to use if in dict
    # or we make a set of candidates in job and applications in job who have prosepect False
    # then present that revised list for them to make selection, we need is the app_id  and the stage_id of current 

    print 'Under Construction'

def users_menu():
    # add user
    def add_user():

        # select user to add on behalf of 
        raw_input('First select SiteAdmin to perform action [Enter to continue]')
        # make initial call to get list of users
        u_ls, n_page = get_list(burl, 'users')

        # prompt selection of users to send on-behalf-of
        obo_obj = next_page_one(u_ls, n_page)

        obo_id_str = str(obo_obj['id'])

        # loop  to create users until break
        add_u = True

        while add_u:

            data = {}

            data['first_name'] = raw_input('First Name: ').strip()

            data['last_name'] = raw_input('Last Name: ').strip()

            data['email'] = raw_input('users email: ').strip()

            data['send_email_invite'] = True 

            data_u = json.dumps(data)

            u_req = urllib2.Request(burl + 'users', data_u)

            u_req.add_header('Authorization', api)

            u_req.add_header('On-Behalf-Of', obo_id_str)

            try:

                handle = urllib2.urlopen(u_req)

                x_rate_hdr = dict(handle.info())    
                
                if int(x_rate_hdr['x-ratelimit-remaining']) == 0:
            
                    # if 0 time.sleep(10)
                    time.sleep(10)
        
                else:
                    pass

            except (urllib2.HTTPError, urllib2.URLError) as e:
                print e.info()
                print e.read()

            
            add_u = raw_input('Add another user? Y/n: ').strip()

            if add_u.lower() == 'y':

                pass
            
            else:

                add_u = False

    
    def add_bulk_user():

        print 'Under Construction'        

    # add user bulk? 
    # disable users?
    options = [('add a user', add_user), ('add bulk user', add_bulk_user)]

    for each in options:
        # show each option with a number to assign to it
        print str(options.index(each)) + ': ' + each[0]

    try:
        # test answer for existence in list of choices 
        user_choice = int(raw_input('select category by number> ').strip())

        if (user_choice > len(options) - 1) or user_choice < 0:
            
            user_choice = int(raw_input('# not in list> ').strip())

    except ValueError:
        # prompt for a number in case of a non covertable response
        user_choice = int(raw_input('number in menu only> '))

    # return string with the name of the option, need to create sub menus for each of these options an possibly call that instead of return something
    return options[user_choice][1]()


    # get user to send on behalf of 
    print 'Under Construction'

def offices_menu():
    
    #add office and continue to ask if want more
    def add_office():

        # select user to add on behalf of 
        raw_input('First select SiteAdmin to perform action [Enter to continue]')
        # make initial call to get list of users
        u_ls, n_page = get_list(burl, 'users')

        # prompt selection of users to send on-behalf-of
        obo_obj = next_page_one(u_ls, n_page)

        obo_id_str = str(obo_obj['id'])

        # loop  to create users until break
        add_o = True


        while add_o:

            data = {}

            data['name'] = raw_input('Office Name: ').strip()

            ask_tier = raw_input('Is it a child office Y/n: ').strip().lower()

            # ability to make department a tier of another
            if ask_tier == 'y':

                o_ls, ne_page = get_list(burl, 'offices')

                 # extra page of jobs if neccessary and return selection for id used in application

                office_obj = next_page_one(o_ls, ne_page)

                data['parent_id'] = office_obj['id']



            else:

                pass 

            data_o = json.dumps(data)

            u_req = urllib2.Request(burl + 'offices', data_o)

            u_req.add_header('Authorization', api)

            u_req.add_header('On-Behalf-Of', obo_id_str)

            try:

                handle = urllib2.urlopen(u_req)

                x_rate_hdr = dict(handle.info())    
                
                if int(x_rate_hdr['x-ratelimit-remaining']) == 0:
            
                    # if 0 time.sleep(10)
                    time.sleep(10)
        
                else:
                    pass

            except (urllib2.HTTPError, urllib2.URLError) as e:
                print e.info()
                print e.read()

            
            add_o = raw_input('Add another Office? Y/n: ').strip()

            if add_o.lower() == 'y':

                pass
            
            else:

                add_o = False

    add_office()






    #print 'Under Construction'

def departments_menu():
    #print 'Under Construction'

    def add_department():

        # select user to add on behalf of 
        raw_input('First select SiteAdmin to perform action [Enter to continue]')
        # make initial call to get list of users
        u_ls, n_page = get_list(burl, 'users')

        # prompt selection of users to send on-behalf-of
        obo_obj = next_page_one(u_ls, n_page)

        obo_id_str = str(obo_obj['id'])

        # loop  to create users until break
        add_d = True


        while add_d:

            data = {}

            data['name'] = raw_input('Department Name: ').strip()

            ask_tier = raw_input('Is it a child Department Y/n: ').strip().lower()

            # ability to make department a tier of another
            if ask_tier == 'y':

                d_ls, ne_page = get_list(burl, 'departments')

                 # extra page of jobs if neccessary and return selection for id used in application

                department_obj = next_page_one(d_ls, ne_page)

                data['parent_id'] = department_obj['id']



            else:

                pass 

            data_d = json.dumps(data)

            u_req = urllib2.Request(burl + 'departments', data_d)

            u_req.add_header('Authorization', api)

            u_req.add_header('On-Behalf-Of', obo_id_str)

            try:

                handle = urllib2.urlopen(u_req)

                x_rate_hdr = dict(handle.info())    
                
                if int(x_rate_hdr['x-ratelimit-remaining']) == 0:
            
                    # if 0 time.sleep(10)
                    time.sleep(10)
        
                else:
                    pass

            except (urllib2.HTTPError, urllib2.URLError) as e:
                print e.info()
                print e.read()

            
            add_d = raw_input('Add another Department? Y/n: ').strip()

            if add_d.lower() == 'y':

                pass
            
            else:

                add_d = False

    add_department()


def tracking_link():

    # collect token from user to search data
    token = raw_input('''Enter tracking "token" [part after grnh.se/] : ''').strip()

    tl_req = urllib2.Request(burl + 'tracking_links/' + token)

    tl_req.add_header('Authorization', api)

    try:
        tl_handle = urllib2.urlopen(tl_req)

        x_rate_hdr = dict(tl_handle.info())

        if int(x_rate_hdr['x-ratelimit-remaining']) == 0:
            
                    # if 0 time.sleep(10)
                    time.sleep(10)


    except (urllib2.HTTPError, urllib2.URLError) as e:
                print e.info()
                print e.read()

    
    tl_handle = tl_handle.read()

    tl_handle = json.loads(tl_handle)
    
    # print each key and its value
    for each in tl_handle.keys():
        print each + ': ' + str(tl_handle[each])
    #tl_handle = json.load(tl_handle)

    #for each in tl_handle.values():

        #print str(each)


main_menu()
    





# need to delete lists of candidiates 
# need to add ranges of candidates option to name option to do bulk
# better handling of data payload on candidate POST
# advance applications 

