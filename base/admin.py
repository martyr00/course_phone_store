from django.contrib import admin

from base.models import *

admin.site.register(UserProfile)
admin.site.register(Telephone)
admin.site.register(TelephoneImage)
admin.site.register(Brand)
admin.site.register(City)
admin.site.register(Vendor)
admin.site.register(Delivery)
admin.site.register(delivery_details)
admin.site.register(Order)
admin.site.register(order_product_details)
