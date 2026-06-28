item={
     'url': 'https://realtylink.org/en/house~for-rent~vancouver/263156536', 
     'unit_address': '\n                                                1886 E 52ave Vancouver, Killarney VE, Vancouver\n                                            ', 
     'unit_price': '2000', 
     'sqr_feet': '\n                670 sqft\n            ', 
     'description': '\n                                       Bright and functional 2-bedroom, 1-bathroom suite offering approximately 670 sq.ft. of living space. Features a spacious living room, private entrance, and convenient location close to transit, schools, shopping, and daily amenities.  Rental Terms $2,000/month Utilities Included No Pets No Smoking, Vaping, or Drugs Tenant Insurance Required  Please provide: Full Name, Occupation, Number of Occupants, Desired Move-in Date, Lease Term, and a Brief Introduction.  Only Complete Inquiries Containing All Requested Information Will Receive a Response.\n                                            ', 
     'msl_numer': 'R3134909',
     'bed': '2 bedrooms',
     'bath': '1 bathroom',
     'first_pic': 'https://media.realtylink.org/images/consumersite/property/263156536/aece905e67134d24b3c1541444def103.jpeg?width=640&height=480&fit=cover',
     'property_metadata': {
          'Floor Area': '\n                670 sqft\n            ', 
          'Interior Features': None, 'Laundry Features': None, 'Appliances': None, 'Exterior Features': None, 'Parking Spaces': None, 'Amenities': None, 'Cooling Features': None, 'Bylaws Restriction': None}
          }

x=item["unit_address"].replace("\n","").strip()

address= x.split(",")[0]
general_area= x.split(",")[1]
city= x.split(",")[2]

print(
address,
general_area,
city,

)