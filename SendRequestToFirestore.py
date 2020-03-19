def sendVehiclePlateToFirestore(vehiclePlate):

    import firebase_admin
    from firebase_admin import credentials
    from firebase_admin import firestore
    import time
    from datetime import datetime, timedelta

    db = firestore.client()
    now = datetime.now()
    current_date = now.strftime('%d-%m-%Y')
    current_time = now.strftime('%H:%M')

    ticketStartTime = ''
    ticketEndTime = ''

    todays_ticket = db.collection(u'Tickets').where(u'vehiclePlate',u'==', vehiclePlate).where(u'currentDate', u'==', current_date).order_by(u'endTime', direction=firestore.Query.DESCENDING).limit(1)
    docs = todays_ticket.stream()

    for doc in docs:
        #print(u'{} => {}'.format(doc.id, doc.to_dict()))
        ticketStartTime = doc.get('startTime')
        ticketEndTime = doc.get('endTime')

    if ticketStartTime == '':
        return 'no ticket'
    else:
        T_StartTime = datetime.strptime(ticketStartTime, '%H:%M')
        T_EndTime = datetime.strptime(ticketEndTime, '%H:%M')
        T_Now = datetime.strptime(current_time, '%H:%M')

        differenceStartTime = (T_StartTime - T_Now)
        differenceEndTime = (T_EndTime - T_Now)

        outDifferenceStartTime = differenceStartTime.total_seconds()/60
        outDifferenceEndTime =  differenceEndTime.total_seconds()/60

        if (outDifferenceStartTime < 0 and outDifferenceEndTime < 0):
            return 'ticket expired'
        if (outDifferenceStartTime < 0 and outDifferenceEndTime > 0):
            return 'ticket valid'
        if (outDifferenceStartTime > 0 and outDifferenceEndTime > 0):
            return 'future ticket'