import luxurynitro

api = luxurynitro.Client(api_key='api_****')

# print user's credits
print(api.get_credits().total) # 6

# get the current queue
queue = api.get_queue()

# how long the queue is (in amount of claims)
print(queue.length) # 30

# first order in queue
print(queue.queue[0]) # Order(claimed=[], id='0372', eta=ETA(..), quantity=20, received=7, status=Status(..), user=PublicUser(..), timestamp=None)

# most recent claimed nitro
print(queue.recent[0].nitro_type) # Nitro(_type='Basic Monthly', boost=False, classic=False, basic=True, yearly=False, monthly=True)