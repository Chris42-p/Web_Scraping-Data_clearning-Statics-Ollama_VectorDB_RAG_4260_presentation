#this is the interface the spiders should use by default

#should be using the object in this class to mape spider objects into and save into local DB. 


class SpiderData_Default_Obj():
     def __init__(self,                  
title, price, address, street_address, neighbourhood, city, province, bedrooms, bathrooms, square_feet, lot_size, property_type, features, facilities, agent_name, brokerage, listing_url, source_website, first_seen, last_seen, status
     ):
          #== Meta: about the post 
          self.title=title 
          self.listing_url=listing_url 
          self.source_website=source_website 
          self.img_of_unit=img_of_unit

          #== Market speed
          self.days_ago_posted=days_ago_posted
          self.post_updated= post_updated
          self.first_seen=first_seen 
          self.last_seen=last_seen 
          self.status=status 

          #== Address of the home
          self.address=address 
          self.street_address=street_address 
          self.neighbourhood=neighbourhood 
          self.city=city 
          self.province=province 
          
          #== About the unit
          self.price=price 
          self.bedrooms=bedrooms 
          self.bathrooms=bathrooms 
          self.square_feet=square_feet 
          self.lot_size=lot_size 
          self.property_type=property_type 
          self.post_description=post_description
          self.move_in_date=move_in_date
          self.security_deposit=security_deposit
          self.min_rental_period=min_rental_period

          #== Features
          self.ameneties=amenties #make this a list
          self.features=features 
          self.facilities=facilities 
          self.pet=pet
          self.appliances=appliances #laundry, stove, dishwasher, washer, dryer
          self.parking=parking
          self.locker=locker
          self.smoking=smoking

          #== seller info 
          self.agent_name=agent_name 
          self.brokerage=brokerage 

          