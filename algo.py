#this is the algorithm to have an increasing or decreasing density



def algo(w,t):
    if(w < t):
        week_list = [int(w/t)]*w
    else:
        week_list = [0]*w
    return week_list

def getDistribution(weeks,topics):
    orignal_topics = topics
    hard_week = algo(weeks,topics)
    wm = weeks
    topics -= sum(hard_week)
    #print("hard_week", hard_week)
    h = topics 
    H = h
    
    
    
    end = wm
    total = sum(hard_week)
    while h > 0:
        #print(hard_week)
        if(h%2!=0 and h!=1):
            h += 1
        h = round(h/2)

        if h==1:
            break;
        
        if(end==0):
            break
        que = round(h/end)
        if(que== 0):
            que=1
        for x in range(0,end):
            hard_week[x] += que
            if(sum(hard_week) == H ):
                break
        end = round(end/2)
        if(sum(hard_week) == H ):
            break
           
        total += h


    if orignal_topics > sum(hard_week):
        hard_week[0] += orignal_topics - sum(hard_week)
    else:
        hard_week[0] -= sum(hard_week) - orignal_topics

    print("total weeks: ", wm)
    print("total topics: ",orignal_topics)
    print("distributed topics: ", sum(hard_week))
    return hard_week
    '''
    while sum(hard_week) < H:
        for x in range(wm):
            if sum(hard_week) > H:
                break
            hard_week[x] += 1

            
    if(sum(hard_week) > H):
        hard_week[0] -= (sum(hard_week) - H)
    else:
        hard_week[0] += (H - sum(hard_week))

    print("total weeks: ", wm)
    print("total topics: ",H)
    print("distributed topics: ", sum(hard_week))
    return hard_week
    '''




        
#print(getDistribution(weeks=25,topics=200))

    
    
   

