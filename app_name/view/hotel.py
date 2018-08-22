# -*- coding: utf-8 -*-

from cta.model.hotel import Hotel, Amenity, Image, Deal, Website, Facility, Member, Room, HotelCollection, CollectionProduct
from cta import app
from sqlalchemy import or_
from flask import jsonify, request
from cta.schema.hotel import HotelSchema, AmenitySchema, ImageSchema, DealSchema, WebsiteSchema, FacilitySchema, MemberSchema, RoomSchema, HotelCollectionSchema, CollectionProductSchema
import datetime
from itertools import cycle
import simplejson as json


@app.route('/api/v1/hotel', methods=['GET', 'POST'])
def hotel_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        rating = request.args.get('rating')
        args.pop('rating', None)
        check_in = request.args.get('check_in')
        check_out = request.args.get('check_out')
        price_start = request.args.get('price_start', None)
        price_end = request.args.get('price_end', None)
        args.pop('price_start', None)
        args.pop('price_end', None)
        page = request.args.get('page', None)
        per_page = request.args.get('per_page', None)
        hotel_room_id = []
        price_hotel_list = []
        weekend_hotel_list = []
        if check_in and check_out:
            no_of_days = int(check_out) - int(check_in)
            sec = datetime.timedelta(seconds=int(no_of_days))
            d = datetime.datetime(1, 1, 1) + sec
            no_of_days = d.day - 1
            check_in = datetime.datetime.fromtimestamp(
                int(check_in)).weekday()
            check_out = datetime.datetime.fromtimestamp(
                int(check_out)).weekday()
            a = [0, 1, 2, 3, 4, 5, 6]
            pool = cycle(a)
            start = False
            days = []
            weekend = False
            for i, val in enumerate(pool):
                if start and val == check_out and len(days) == no_of_days:
                    break
                if start:
                    days.append(val)
                if val == check_in and start is False:
                    start = True
                    days.append(val)
            for day in days:
                if day == 5:
                    weekend = True
                elif day == 6:
                    weekend = True
            deals_list = Deal.query.filter(Deal.weekend == weekend).all()
            for deal_obj in deals_list:
                hotel_room_id.append(deal_obj.room_id)
            room_list = Room.query.filter(Room.id.in_(hotel_room_id)).all()
            for room_obj in room_list:
                weekend_hotel_list.append(room_obj.hotel_id)
            hotels = Hotel.query.filter_by(**args).filter(Hotel.id.in_(weekend_hotel_list)).all()
        elif price_start and price_end:
            deals_list = Deal.query.filter(Deal.price >= price_start, Deal.price <= price_end).all()
            for deal_obj in deals_list:
                hotel_room_id.append(deal_obj.room_id)
            room_list = Room.query.filter(Room.id.in_(hotel_room_id)).all()
            for room_obj in room_list:
                price_hotel_list.append(room_obj.hotel_id)
            hotels = Hotel.query.filter_by(**args).filter(Hotel.id.in_(price_hotel_list)).all()
        elif rating:
            hotels = Hotel.query.filter_by(**args).filter(Hotel.rating >= rating).all()
        elif page and per_page:
            hotels = Hotel.query.filter_by(**args).offset((int(page) - 1) * int(per_page)).limit(int(per_page)).all()
        else:
            hotels = Hotel.query.filter_by(**args).all()
        result = HotelSchema(many=True).dump(hotels)
        return jsonify({'result': {'hotel': result.data}, 'message': "Success", 'error': False})
    else:
        hotel = request.json
        hotel_obj = {
        "name": hotel.get("name", None),
        "is_partner": hotel.get("is_partner", None),
        "city": hotel.get("city", None),
        "category": hotel.get("category", None),
        "phone": hotel.get("phone", None),
        'rating': hotel.get("rating", None),
        "desc": hotel.get("desc", None),
        "address": hotel.get("address", None),
        "longitude": json.dumps(hotel.get("longitude", None)),
        "latitude": json.dumps(hotel.get("latitude", None)),
        "star": hotel.get("star", None),
        }
        post = Hotel(**hotel_obj)
        post.save()
        hotel_result = HotelSchema().dump(post)
        if hotel.get("collection"):
            collection = hotel.get("collection", None)
            collection_obj = {
                "hotel_id": hotel_result.data['id'],
                "collection_name": collection.get("collection_name", None),
                "featured": collection.get("featured", None),
                "desc": collection.get("desc", None),
                "image": collection.get("image", None),
            }
            post = HotelCollection(**collection_obj)
            post.save()
            collection_result = HotelCollectionSchema().dump(post)
            if collection.get("products"):
                products = collection.get("products")
                for product in products:
                    product_obj = {
                        "hotel_collection_id": collection_result.data['id'],
                        "product_name": product.get("product_name", None),
                        "product_url": product.get("product_url", None),
                        "featured_product": product.get("featured_product", None),
                        "product_desc": product.get("product_desc", None),
                        "product_image": product.get("product_image", None),
                    }
                    post = CollectionProduct(**product_obj)
                    post.save()
        if hotel.get("amenities"):
            amenity = hotel.get("amenities", None)
            amenity_obj = {
                "hotel_id": hotel_result.data['id'],
                "Room_cleaning_service": amenity.get("Room_cleaning_service", None),
                "parking": amenity.get("parking", None),
                "couple_friendly": amenity.get("couple_friendly", None),
                "banquets": amenity.get("banquets", None),
                "bar": amenity.get("bar", None),
                "child_baby_cot": amenity.get("child_baby_cot", None),
                "conference_room": amenity.get("conference_room", None),
                "doorman": amenity.get("doorman", None),
                "express_check_in_out": amenity.get("express_check_in_out", None),
                "gym": amenity.get("gym", None),
                "hairdresser": amenity.get("hairdresser", None),
                "indoor_swimming_pool": amenity.get("indoor_swimming_pool", None),
                "laundry_service": amenity.get("laundry_service", None),
                "lift": amenity.get("lift", None),
                "non_smoking_smoking_rooms": amenity.get("non_smoking_smoking_rooms", None),
                "outdoor_swimming_pool": amenity.get("outdoor_swimming_pool", None),
                "pet_allowance": amenity.get("pet_allowance", None),
                "pool": amenity.get("pool", None),
                "porter_service": amenity.get("porter_service", None),
                "restaurant": amenity.get("restaurant", None),
                "spa": amenity.get("spa", None),
                "terrace": amenity.get("terrace", None),
                "twenty_four_hr_reception": amenity.get("twenty_four_hr_reception", None),
                "twenty_four_hr_room_service": amenity.get("twenty_four_hr_room_service", None),
                "wheelchair_accessible": amenity.get("wheelchair_accessible", None),
                "wifi_in_lobby": amenity.get("wifi_in_lobby", None)
            }
            Amenity(**amenity_obj).save()
        if hotel.get("images"):
            for image in hotel['images']:
                image_obj = {
                    "image_url": image.get("image_url", None),
                    "hotel_id": hotel_result.data['id']
                }
                Image(**image_obj).save()
        return jsonify({'result': {'hotel': hotel_result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/hotel/<int:id>', methods=['PUT', 'DELETE'])
def hotel_id(id):
    if request.method == 'PUT':
        print(request.json)
        put = Hotel.query.filter_by(id=id).update(request.json)
        if put:
            Hotel.update_db()
            hotels = Hotel.query.filter_by(id=id).first()
            result = HotelSchema(many=False).dump(hotels)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    elif request.method == 'DELETE':
        hotel = Hotel.query.filter_by(id=id).first()
        if not hotel:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        Amenity.query.filter_by(hotel_id=id).delete()
        Image.query.filter_by(hotel_id=id).delete()
        collection = HotelCollection.query.filter_by(hotel_id=id).first()
        if collection:
            CollectionProduct.query.filter_by(hotel_collection_id=collection.id).delete()
            HotelCollection.delete_db(collection)
        rooms = Room.query.filter_by(hotel_id=id).all()
        if rooms:
            for room in rooms:
                Facility.query.filter_by(room_id=room.id).delete()
                Member.query.filter_by(room_id=room.id).delete()
                Deal.query.filter_by(room_id=room.id).delete()
                Room.delete_db(room)
        Hotel.delete_db(hotel)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/api/v1/hotel/collection', methods=['GET', 'POST'])
def hotel_collection_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        data = HotelCollection.query.filter_by(**args).all()
        result = HotelCollectionSchema(many=True).dump(data)
        return jsonify({'result': {'collection': result.data}, 'message': "Success", 'error': False})
    else:
        post = HotelCollection(**request.json)
        post.save()
        result = HotelCollectionSchema().dump(post)
        return jsonify({'result': {'collection': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/hotel/collection/<int:id>', methods=['PUT', 'DELETE'])
def hotel_collection_id(id):
    if request.method == 'PUT':
        put = HotelCollection.query.filter_by(id=id).update(request.json)
        if put:
            HotelCollection.update_db()
            s = HotelCollection.query.filter_by(id=id).first()
            result = HotelCollectionSchema(many=False).dump(s)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        collection = HotelCollection.query.filter_by(id=id).first()
        if not collection:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        else:
            CollectionProduct.query.filter_by(hotel_collection_id=collection.id).delete()
            HotelCollection.delete_db(collection)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/api/v1/hotel/collection/product', methods=['GET', 'POST'])
def collection_product_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        data = CollectionProduct.query.filter_by(**args).all()
        result = CollectionProductSchema(many=True).dump(data)
        return jsonify({'result': {'products': result.data}, 'message': "Success", 'error': False})
    else:
        post = CollectionProduct(**request.json)
        post.save()
        result = CollectionProductSchema().dump(post)
        return jsonify({'result': {'products': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/hotel/collection/product/<int:id>', methods=['PUT', 'DELETE'])
def collection_product_id(id):
    if request.method == 'PUT':
        put = CollectionProduct.query.filter_by(id=id).update(request.json)
        if put:
            CollectionProduct.update_db()
            s = CollectionProduct.query.filter_by(id=id).first()
            result = HotelCollectionSchema(many=False).dump(s)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        collection_product = CollectionProduct.query.filter_by(id=id).first()
        if not collection_product:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        CollectionProduct.delete_db(collection_product)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/api/v1/room', methods=['GET', 'POST'])
def room_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        rooms = Room.query.filter_by(**args).all()
        result = RoomSchema(many=True).dump(rooms)
        return jsonify({'result': {'rooms': result.data}, 'message': "Success", 'error': False})
    else:
        room = request.json
        room_obj = {
            "room_type": room.get("room_type", None),
            "other_room_type": room.get("other_room_type", None),
            "image_url": room.get("image_url", None),
            "check_in": datetime.datetime.now(),
            "check_out": datetime.datetime.now(),
            "status": True,
            "breakfast": room.get("breakfast", None),
            "balcony": room.get("ac", None),
            "hotel_id": room.get("hotel_id", None)
        }
        post = Room(**room_obj)
        post.save()
        room_result = RoomSchema().dump(post)
        member = room.get("member", None)
        if member:
            member_obj = {
                "no_of_adults": member.get("no_of_adults", None),
                "total_members": member.get("total_members", None),
                "children": member.get("children", None),
                "room_id": room_result.data['id'],
            }
            Member(**member_obj).save()
        facility = room.get("facilities", None)
        if facility:
            facility_obj = {
                "room_id": room_result.data['id'],
                "ac": facility.get("ac", None),
                "bed_type": facility.get("bed_type", None),
                "no_of_bed": facility.get("no_of_bed", None),
                "bathroom_cosmetics": facility.get("bathroom_cosmetics", None),
                "bathroom_nightie": facility.get("bathroom_nightie", None),
                "bathroom_towels": facility.get("bathroom_towels", None),
                "bathroom_with_shower": facility.get("bathroom_with_shower", None),
                "desk": facility.get("desk", None),
                "electric_kettle": facility.get("electric_kettle", None),
                "fan": facility.get("fan", None),
                "food_serve_at_room": facility.get("food_serve_at_room", None),
                "free_evening_snacks": facility.get("free_evening_snacks", None),
                "free_toiletries": facility.get("free_toiletries", None),
                "hairdryer": facility.get("hairdryer", None),
                "heater": facility.get("heater", None),
                "ironing_facility": facility.get("ironing_facility", None),
                "morning_newspaper": facility.get("morning_newspaper", None),
                "phone": facility.get("phone", None),
                "room_safe": facility.get("room_safe", None),
                "room_seating_area": facility.get("room_seating_area", None),
                "room_slipper": facility.get("room_slipper", None),
                "tv": facility.get("tv", None),
                "view": facility.get("view", None),
                "wardrobes_closet": facility.get("wardrobes_closet", None),
                "weighing_machine": facility.get("weighing_machine", None),
                "wifi": facility.get("wifi", None)
            }
            Facility(**facility_obj).save()
        if room.get('deals'):
            for deal in room['deals']:
                deal_obj = {
                    "price": deal.get("price", None),
                    "weekend": deal.get("weekend", None),
                    "hotel_url": deal.get("hotel_url", None),
                    "room_id": room_result.data['id'],
                    "website_id": deal.get("website_id", None)
                }
                Deal(**deal_obj).save()
        return jsonify({'result': {'room': request.json}, 'message': "Success", 'error': False})


@app.route('/api/v1/room/<int:id>', methods=['PUT', 'DELETE'])
def room_id(id):
    if request.method == 'PUT':
        put = Room.query.filter_by(id=id).update(request.json)
        if put:
            Room.update_db()
            s = Room.query.filter_by(id=id).first()
            result = RoomSchema(many=False).dump(s)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        rooms = Room.query.filter_by(id=id).first()
        if not rooms:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        Facility.query.filter_by(room_id=id).delete()
        Member.query.filter_by(room_id=id).delete()
        Deal.query.filter_by(room_id=id).delete()
        Room.delete_db(rooms)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/api/v1/amenity', methods=['GET', 'POST'])
def amenity_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        data = Amenity.query.filter_by(**args).offset((page - 1) * per_page).limit(per_page).all()
        result = AmenitySchema(many=True).dump(data)
        return jsonify({'result': {'amenities': result.data}, 'message': "Success", 'error': False})
    else:
        post = Amenity(**request.json)
        post.save()
        result = AmenitySchema().dump(post)
        return jsonify({'result': {'amenities': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/amenity/<int:id>', methods=['PUT', 'DELETE'])
def amenity_id(id):
    if request.method == 'PUT':
        put = Amenity.query.filter_by(id=id).update(request.json)
        if put:
            Amenity.update_db()
            s = Amenity.query.filter_by(id=id).first()
            result = AmenitySchema(many=False).dump(s)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        amenities = Amenity.query.filter_by(id=id).first()
        if not amenities:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        Amenity.delete_db(amenities)
        return jsonify({'result': {}, 'message': "Success", 'error': False})



@app.route('/api/v1/image', methods=['GET', 'POST'])
def image_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        data = Image.query.filter_by(**args).offset((page - 1) * per_page).limit(per_page).all()
        result = ImageSchema(many=True).dump(data)
        return jsonify({'result': {'images': result.data}, 'message': "Success", 'error': False})
    else:
        post = Image(**request.json)
        post.save()
        result = ImageSchema().dump(post)
        return jsonify({'result': {'image': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/image/<int:id>', methods=['PUT', 'DELETE'])
def image_id(id):
    if request.method == 'PUT':
        put = Image.query.filter_by(id=id).update(request.json)
        if put:
            Image.update_db()
            s = Image.query.filter_by(id=id).first()
            result = ImageSchema(many=False).dump(s)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        images = Image.query.filter_by(id=id).first()
        if not images:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        Image.delete_db(images)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/api/v1/member', methods=['GET', 'POST'])
def member_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        members = Member.query.filter_by(**args).offset((page - 1) * per_page).limit(per_page).all()
        result = MemberSchema(many=True).dump(members)
        return jsonify({'result': {'members': result.data}, 'message': "Success", 'error': False})
    else:
        post = Member(**request.json)
        post.save()
        result = MemberSchema().dump(post)
        return jsonify({'result': {'member': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/member/<int:id>', methods=['PUT', 'DELETE'])
def member_id(id):
    if request.method == 'PUT':
        put = Member.query.filter_by(id=id).update(request.json)
        if put:
            Member.update_db()
            s = Member.query.filter_by(id=id).first()
            result = MemberSchema(many=False).dump(s)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        members = Member.query.filter_by(id=id).first()
        if not members:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        Member.delete_db(members)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/api/v1/facility', methods=['GET', 'POST'])
def facility_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        data = Facility.query.filter_by(**args).offset((page - 1) * per_page).limit(per_page).all()
        result = FacilitySchema(many=True).dump(data)
        return jsonify({'result': {'facilities': result.data}, 'message': "Success", 'error': False})
    else:
        post = Facility(**request.json)
        post.save()
        result = FacilitySchema().dump(post)
        return jsonify({'result': {'facilities': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/facility/<int:id>', methods=['PUT', 'DELETE'])
def facility_id(id):
    if request.method == 'PUT':
        print(request.json)
        put = Facility.query.filter_by(id=id).update(request.json)
        if put:
            Facility.update_db()
            s = Facility.query.filter_by(id=id).first()
            result = FacilitySchema(many=False).dump(s)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        data = Facility.query.filter_by(id=id).first()
        if not data:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        Facility.delete_db(data)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/api/v1/website', methods=['GET', 'POST'])
def website_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        web = Website.query.filter_by(**args).all()
        result = WebsiteSchema(many=True).dump(web)
        return jsonify({'result': {'website': result.data}, 'message': "Success", 'error': False})
    else:
        post = Website(**request.json)
        post.save()
        result = WebsiteSchema().dump(post)
        return jsonify({'result': {'website': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/deal', methods=['GET', 'POST'])
def deal_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        check_in = request.args.get('check_in')
        check_out = request.args.get('check_out')
        no_of_days = 1
        price_start = request.args.get('price_start', None)
        price_end = request.args.get('price_end', None)
        args.pop('price_start', None)
        args.pop('price_end', None)
        hotel_id = request.args.get('hotel_id', None)
        args.pop('hotel_id', None)
        if check_in and check_out:
            no_of_days = int(check_out) - int(check_in)
            sec = datetime.timedelta(seconds=int(no_of_days))
            d = datetime.datetime(1, 1, 1) + sec
            no_of_days = d.day - 1
            check_in = datetime.datetime.fromtimestamp(
                int(check_in)).weekday()
            check_out = datetime.datetime.fromtimestamp(
                int(check_out)).weekday()
            a = [0, 1, 2, 3, 4, 5, 6]
            pool = cycle(a)
            start = False
            days = []
            weekend = False
            for i, val in enumerate(pool):
                if start and val == check_out and len(days) == no_of_days:
                    break
                if start:
                    days.append(val)
                if val == check_in and start is False:
                    start = True
                    days.append(val)
            for day in days:
                if day == 5:
                    weekend = True
                elif day == 6:
                    weekend = True
            args['weekend'] = weekend
        args.pop('page', None)
        args.pop('per_page', None)
        args.pop('check_in', None)
        args.pop('check_out', None)
        hotel_room_id = []
        price = []
        if hotel_id:
            rooms_list = Room.query.filter(Room.hotel_id == hotel_id).all()
            for room_obj in rooms_list:
                hotel_room_id.append(room_obj.id)
                price = Deal.query.filter_by(**args).filter(Deal.room_id.in_(hotel_room_id)).all()
        elif price_start and price_end:
            price = Deal.query.filter_by(**args)\
                .filter(Deal.price >= price_start, Deal.price <= price_end).all()
        else:
            price = Deal.query.filter_by(**args).all()
        result = DealSchema(many=True).dump(price)
        for deal in result.data:
            # if deal["room"]:
            #     deal["hotel_id"] = Room.query.filter(Room.id == deal["room"]).first().hotel_id
            if no_of_days >= 1 and deal['price']:
                deal['price'] = int(deal["price"]) * no_of_days
        return jsonify({'result': {'deal': result.data}, 'message': "Success", 'error': False})
    else:
        post = Deal(**request.json)
        post.save()
        result = DealSchema().dump(post)
        return jsonify({'result': {'deal': result.data}, 'message': 'Success', 'error': False})


@app.route('/api/v1/deal/<int:id>', methods=['PUT', 'DELETE'])
def deal_id(id):
    if request.method == 'PUT':
        put = Deal.query.filter_by(id=id).update(request.json)
        if put:
            Deal.update_db()
            data = Deal.query.filter_by(id=id).first()
            result = DealSchema(many=False).dump(data)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        data = Deal.query.filter_by(id=id).first()
        if not data:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        Deal.delete_db(data)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/hotel/search', methods=['GET', 'POST'])
def hotel_search():
    search = request.json
    search = search['search']
    cities = []
    names = []
    hotel_cities = Hotel.query.distinct(Hotel.city).filter(Hotel.city.like('%' + search + '%')).order_by(Hotel.city).all()
    for hotel_city in hotel_cities:
        cities.append(hotel_city.city)
    hotel_names = Hotel.query.distinct(Hotel.name).filter(Hotel.name.like('%' + search + '%')).order_by(Hotel.name).all()
    for hotel_name in hotel_names:
        names.append(hotel_name.name)
    return jsonify({'result': {'cities': cities, "names": names}, 'message': "Success", 'error': False})