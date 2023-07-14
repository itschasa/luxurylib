from . import http_client
from . import classes
from . import errors

class Client():
    def __init__(self, api_key: str, base_url='https://nitro.luxuryservices.cc/api/v1', *args) -> None:
        self.api_key = api_key
        self._base_url = base_url
        
        self.client = http_client.HTTP(
            api_key=api_key,
            base_url=base_url,
            *args
        )

        self._public_user = None
        
    def get_user(self) -> classes.User:
        res = self.client.get('/users/@me')
        resjson = res.json()
        
        self._public_user = classes.PublicUser(
            display_name = resjson['display_name'],
            id = resjson['id']
        )
        
        return classes.User(
            username = resjson['username'],
            display_name = resjson['display_name'],
            email = resjson['email'],
            id = resjson['id'],
            credits = resjson['credits'],
            orders = [
                classes.Order(
                    eta = classes.ETA(
                        next_gift = order['eta'].get('next'),
                        completed = order['eta'].get('completed'),
                    ),
                    claimed = [
                        classes.Claim(
                            instance = claim['instance'],
                            timestamp = claim['time'],
                            nitro_type = classes.Nitro(
                                _type = claim['type']
                            ),
                            user = self._public_user,
                            order_id = order['id']
                        ) for claim in order['claimed']
                    ],
                    id = order['id'],
                    quantity = order['quantity'],
                    received = order['received'],
                    status = classes.Status(
                        _type = order['status'],
                        status_text = order['status_text']
                    ),
                    timestamp = order['time'],
                    user = self._public_user
                ) for order in resjson['orders']
            ],
            stats = classes.Stats(
                alts = resjson['stats']['alts'],
                boost_chance = resjson['stats']['boost_percent'],
                servers = resjson['stats']['servers'],
                support_time = resjson['stats']['support_time'],
                total_claims = resjson['stats']['total_claims'],
            ),
            tickets = [
                classes.Ticket(
                    timestamp = ticket['creation_time'],
                    id = ticket['id'],
                    opened = ticket['open'],
                    seen = ticket['seen']
                ) for ticket in resjson['tickets']
            ]
        )
    
    def get_queue(self) -> classes.Queue:
        res = self.client.get('/queue')
        resjson = res.json()

        return classes.Queue(
            eta = classes.ETA(
                next_gift = resjson['eta_per_gift'],
                completed = resjson['queue_cleared']
            ),
            length = resjson['queue_quantity'],
            queue = [
                classes.Order(
                    eta = classes.ETA(
                        next_gift = order['eta'].get('next'),
                        completed = order['eta'].get('completed'),
                    ),
                    claimed = [],
                    id = order['id'],
                    quantity = order['quantity'],
                    received = order['received'],
                    status = classes.Status(
                        _type = order['status']
                    ),
                    user = classes.PublicUser(
                        display_name = order['user']['display_name'],
                        id = order['user']['id'],
                    )
                ) for order in resjson['queue']
            ],
            recent = [
                classes.Claim(
                    timestamp = claim['time'],
                    nitro_type = classes.Nitro(
                        _type = claim['type']
                    ),
                    user = classes.PublicUser(
                        display_name = claim['user']['display_name'],
                        id = claim['user']['id']
                    ),
                    order_id = claim['order']
                ) for claim in resjson['recent']
            ]
        )
    
    def get_credits(self) -> classes.Credits:
        res = self.client.get('/users/@me/credits')
        resjson = res.json()

        return classes.Credits(
            total = resjson['total'],
            history = [
                classes.CreditChange(
                    change = int(change['change']),
                    closing_balance = change['closing_balance'],
                    id = change['id'],
                    reason = change['reason'],
                    timestamp = change['time']
                ) for change in resjson['history']
            ]
        )
    
    def get_tickets(self) -> list[classes.Ticket]:
        res = self.client.get('/users/@me/tickets')
        resjson = res.json()

        return [
            classes.Ticket(
                timestamp = ticket['creation_time'],
                id = ticket['id'],
                opened = ticket['open'],
                seen = ticket['seen']
            ) for ticket in resjson
        ]
    
    def get_orders(self) -> list[classes.Order]:
        res = self.client.get('/users/@me/orders')
        resjson = res.json()

        return [
            classes.Order(
                eta = classes.ETA(
                    next_gift = order['eta'].get('next'),
                    completed = order['eta'].get('completed'),
                ),
                claimed = [
                    classes.Claim(
                        instance = claim['instance'],
                        timestamp = claim['time'],
                        nitro_type = classes.Nitro(
                            _type = claim['type']
                        ),
                        user = self._public_user,
                        order_id = order['id']
                    ) for claim in order['claimed']
                ],
                id = order['id'],
                quantity = order['quantity'],
                received = order['received'],
                status = classes.Status(
                    _type = order['status'],
                    status_text = order['status_text']
                ),
                timestamp = order['time'],
                user = self._public_user
            ) for order in resjson
        ]
    
    def create_order(self, quantity:int, token:str, anonymous:bool=False, reason:str='') -> classes.Order:
        res = self.client.post('/users/@me/orders',
            json = {
                'quantity': quantity,
                'token': token,
                'anonymous': anonymous,
                'reason': reason
            }
        )
        order_id = res.json()['order']

        for order in self.get_orders():
            if order.id == order_id:
                return order

    def delete_order(self, order:classes.Order=None, order_id:str=None):
        if order is None and order_id is None:
            raise errors.ValidationError("one argument has to be not None")
        
        self.client.delete(f'/users/@me/orders/{order.id if order is not None else order_id}')

