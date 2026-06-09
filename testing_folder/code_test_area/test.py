from bs4 import BeautifulSoup
import re


class XX():
     content={'post_id': 'post id: 7933065454', 'time_of_post': '2026-05-08T14:52:55-0700', 'user_post_title': 'Garden level suite with spectacular view, 2 bed, 2 bath.', 'first_pic': 'https://images.craigslist.org/00202_aMWkT5dcbzW_0CI0t2_600x450.jpg', 'user_meta_tags': '<div class="attrgroup">\n\n\n            <div class="attr">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?housing_type=6">house</a>\n</span>\n            </div>\n\n\n            <div class="attr">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?laundry=1">w/d in unit</a>\n</span>\n            </div>\n\n\n            <div class="attr">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?parking=5">street parking</a>\n</span>\n            </div>\n\n\n            <div class="attr no_smoking">\n                <span class="valu">              <a href="https://vancouver.craigslist.org/search/apa?no_smoking=1">no smoking</a>\n</span>\n            </div>\n    </div>', 'post_url': 'https://vancouver.craigslist.org/nvn/apa/d/west-vancouver-garden-level-suite-with/7933065454.html', 'price_of_the_unit': '$4,000', 'num_bedrooms_n_square_feet_sq': '/ 2br - 1500ft', 'city_general_area': ' (West Vancouver)', 'address': None, 'bed_and_bath': '<span class="attr important">\n                2BR / 2Ba\n            </span>', 'square_feet_unit': '<span class="attr important">\n                1500ft<sup>2</sup>\n            </span>', 'post_description': '<section id="postingbody">\n        <div class="print-information print-qrcode-container">\n            <p class="print-qrcode-label">QR Code Link to This Post</p>\n            <div class="print-qrcode" data-location="https://vancouver.craigslist.org/nvn/apa/d/west-vancouver-garden-level-suite-with/7933065454.html">\n            </div>\n        </div>\nSpectacular views of downtown Vancouver and Lions Gate from all rooms, located in a prime West Van neighborhood within the Chartwell Elementary and Sentinel Secondary school catchments. This 1,500 sqf garden level suite features high ceiling (9 feet), layout includes 2 large bedrooms, all with bathroom inside (ensuite). All bedrooms and living room have full glass doors from floor to ceiling, opening up to a flat backyard with a swimming pool and spectacular views. Complete privacy with own entrance and own laundry. Parking space for 1 car in the front yard (not in the garage) and additional street parking. Price: $4,000/month, utilities and internet are already included. Available now.<br>\n**No smoking inside. **No pets. **Unfurnished. **Will require references and credit (income) check. **Not accessible by wheelchair. **Utilities are included for up to 4 people, and EV charging is NOT included. **Please email/text for questions or viewing.<br>\n    </section>', 'rent_period': 'monthly'}

     def __init__(self,):
          post_id=self.content["post_id"].strip().split(":")[1]
          # print(post_id)

          time_of_post=self.content["time_of_post"]
          # print(time_of_post)
          
          user_post_title=self.content["user_post_title"]
          # print(user_post_title)


          user_meta_tags= self.__strip_html(self.content["user_meta_tags"]).replace("\n"," ")
          user_meta_tags =self.__strip_extra_spaces(user_meta_tags)
          
          
          # user_meta_tags
          print(user_meta_tags)

          
          
          
          # user_meta_tags=self.content["user_meta_tags"]
          
          
          self.content
          self.content


          pass

     def __strip_extra_spaces(self, text) :
          return re.sub( r"\s+", " ", text)

          
          pass
     def __strip_html(self,text):
          return BeautifulSoup(text, "html.parser").get_text()
          pass




XX()



