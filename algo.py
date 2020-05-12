#this is the algorithm to have an increasing or decreasing density

def getDistribution(weeks,topics):
    wm = weeks
    h = topics 
    H = h
    hard_week = [0]*wm
    
    end = wm
    total = 0
    while h > 0:
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


#print(getDistribution(weeks=100,topics=50))
        


    
    
   

