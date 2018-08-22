from cta.model.cab import Cab, CabAmenity, CabBooking, CabImage, CabDeal, CabTax, CabDealAssociation, CabUser,\
    CabWebsite, CabCollectionProduct, CabCollection
from cta import app, db
from flask import jsonify, request
from cta.lib.cab_fare import CabFare
from cta.schema.cab import CabAmenitySchema, CabBookingSchema, CabImageSchema, CabDealSchema, CabSchema, CabTaxSchema,\
    CabUserSchema, CabWebsiteSchema, CabCollectionProductSchema, CabCollectionSchema
import datetime
from itertools import cycle
import simplejson as json



@app.route('/api/v1/cab', methods=['GET', 'POST'])
def cab_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        rating = request.args.get('rating')
        args.pop('rating', None)
        cab_type = request.args.get('cab_type', None)
        pickup_time = request.args.get('pickup_time', None)
        drop_time = request.args.get('drop_time', None)
        pickup_lat = request.args.get('pickup_lat', None)
        pickup_lon = request.args.get('pickup_lon', None)
        drop_lat = request.args.get('drop_lat', None)
        drop_lon = request.args.get('drop_lon', None)
        args.pop('pickup_time', None)
        args.pop('drop_time', None)
        args.pop('pickup_lat', None)
        args.pop('pickup_lon', None)
        args.pop('drop_lat', None)
        args.pop('drop_lon', None)
        min_base_fare = request.args.get('min_base_fare', None)
        max_base_fare = request.args.get('max_base_fare', None)
        min_total_fare = request.args.get('min_total_fare', None)
        max_total_fare = request.args.get('max_total_fare', None)
        args.pop('min_base_fare', None)
        args.pop('max_base_fare', None)
        args.pop('min_total_fare', None)
        args.pop('max_total_fare', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        args.pop('page', None)
        args.pop('per_page', None)
        q = db.session.query(Cab).outerjoin(Cab.amenities).outerjoin(Cab.deals)
        for key in args:
            if key in Cab.__dict__:
                q = q.filter(getattr(Cab, key) == args[key])
            elif key in CabAmenity.__dict__:
                q = q.filter(getattr(CabAmenity, key) == args[key])
            elif key in CabDeal.__dict__:
                q = q.filter(getattr(CabDeal, key) == args[key])
        if min_base_fare and max_base_fare:
            q = q.filter(CabDeal.base_fare >= min_base_fare, CabDeal.base_fare <= max_base_fare)
        elif min_total_fare and max_total_fare:
            q = q.filter(CabDeal.total_fare >= min_total_fare, CabDeal.total_fare <= max_total_fare)
        elif rating:
            q = q.filter(Cab.rating >= rating)
        data = q.offset((int(page) - 1) * int(per_page)).limit(int(per_page)).all()
        result = CabSchema(many=True).dump(data)
        if pickup_time and drop_time:
            for cab in result.data:
                if cab.get("deals", None):
                    deals = cab.get("deals", None)
                    for deal in deals:
                        fare_obj = {
                            "pickup_time": pickup_time,
                            "drop_time": drop_time,
                            "pickup_lat": pickup_lat,
                            "pickup_lon": pickup_lon,
                            "drop_lat": drop_lat,
                            "drop_lon": drop_lon,
                            "cab_type": cab_type,
                            "base_fare": deal.get('base_fare', None),
                            "one_way": deal.get('one_way', None),
                            "driver_per_hr_allowance_charge": deal.get('driver_per_hr_allowance_charge', None),
                            "slab": deal.get('slab', None),
                            "driver_daily_allowance_charge": deal.get('driver_daily_allowance_charge', None),
                            "car_night_allowance_charge": deal.get('car_night_allowance_charge', None),
                            "base_fare_weekend": deal.get('base_fare_weekend', None),
                            "base_fare_peak_season": deal.get('base_fare_peak_season', None),
                            "base_fare_with_fuel": deal.get('base_fare_with_fuel', None),
                            "different_pickup_drop_point_charge": deal.get('different_pickup_drop_point_charge', None),
                            "fare_exceeded_per_km": deal.get('fare_exceeded_per_km', None),
                            "fare_exceeded_per_hr": deal.get('fare_exceeded_per_hr', None),
                            "initial_km": deal.get('initial_km', None),
                            "initial_km_fare": deal.get('initial_km_fare', None),
                            "km_restriction": deal.get('km_restriction', None),
                            "cancellation_charges": deal.get('cancellation_charges', None),
                        }
                        deal['booking'] = CabFare().fare_calculation(fare_obj)
        return jsonify({'result': {'cabs': result.data}, 'message': "Success", 'error': False})
    else:
        cab = request.json
        deals = cab.get("deals", None)
        images = cab.get("images", None)
        amenities = cab.get("amenities", None)
        cab.pop('amenities', None)
        cab.pop('deals', None)
        cab.pop('images', None)
        cab_post = Cab(**cab)
        cab_post.save()
        for deal in deals:
            if deal.get("deal_id", None):
                assoc_post = CabDealAssociation(cab_id=cab_post.id, deal_id=deal.get("deal_id", None))
                assoc_post.save()
            else:
                website = deal.get("website", None)
                if website:
                    deal.pop('website', None)
                    website_post = CabWebsite(**website)
                    website_post.save()
                    deal["website_id"] = website_post.id
                deal_post = CabDeal(**deal)
                cab_post.deals.append(deal_post)
                deal_post.save()
        for image in images:
            image["cab_id"] = cab_post.id
            image_post = CabImage(**image)
            cab_post.images.append(image_post)
            image_post.save()
        amenities["cab_id"] = cab_post.id
        amenities_post = CabAmenity(**amenities)
        cab_post.amenities = amenities_post
        amenities_post.save()
        result = CabSchema().dump(cab_post)
        return jsonify({'result': {'cab': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/<int:id>', methods=['PUT', 'DELETE'])
def cab_id(id):
    if request.method == 'PUT':
        print(request.json)
        put = Cab.query.filter_by(id=id).update(request.json)
        if put:
            Cab.update_db()
            hotels = Cab.query.filter_by(id=id).first()
            result = CabSchema(many=False).dump(hotels)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        cab = Cab.query.filter_by(id=id).first()
        if not cab:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        CabAmenity.query.filter_by(cab_id=id).delete()
        CabImage.query.filter_by(restaurant_id=id).delete()
        CabDealAssociation.query.filter_by(Cab_id=id).delete()
        Cab.delete_db(cab)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/amenity/<int:id>', methods=['PUT', 'DELETE'])
def cab_amenity_id(id):
    if request.method == 'PUT':
        put = CabAmenity.query.filter_by(id=id).update(request.json)
        if put:
            CabAmenity.update_db()
            s = CabAmenity.query.filter_by(id=id).first()
            result = CabAmenitySchema(many=False).dump(s)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        cab_amenities = CabAmenity.query.filter_by(id=id).first()
        if not cab_amenities:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        CabAmenity.delete_db(cab_amenities)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/amenity', methods=['GET', 'POST'])
def cab_amenity():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        data = CabAmenity.query.filter_by(**args).offset((page - 1) * per_page).limit(per_page).all()
        result = CabAmenitySchema(many=True).dump(data)
        return jsonify({'result': {'amenities': result.data}, 'message': "Success", 'error': False})
    else:
        post = CabAmenity(**request.json)
        post.save()
        result = CabAmenitySchema().dump(post)
        return jsonify({'result': {'amenities': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/user', methods=['GET', 'POST'])
def cab_user():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        data = CabUser.query.filter_by(**args).offset((page - 1) * per_page).limit(per_page).all()
        result = CabUserSchema(many=True).dump(data)
        return jsonify({'result': {'users': result.data}, 'message': "Success", 'error': False})
    else:
        post = CabUser(**request.json)
        post.save()
        result = CabUserSchema().dump(post)
        return jsonify({'result': {'users': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/deal', methods=['GET', 'POST'])
def cab_deal():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        data = CabDeal.query.filter_by(**args).offset((page - 1) * per_page).limit(per_page).all()
        result = CabDealSchema(many=True).dump(data)
        return jsonify({'result': {'deals': result.data}, 'message': "Success", 'error': False})
    else:
        post = CabDeal(**request.json)
        post.save()
        result = CabDealSchema().dump(post)
        return jsonify({'result': {'deals': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/deal/<int:id>', methods=['PUT', 'DELETE'])
def cab_deal_id(id):
    if request.method == 'PUT':
        put = CabDeal.query.filter_by(id=id).update(request.json)
        if put:
            CabDeal.update_db()
            data = CabDeal.query.filter_by(id=id).first()
            result = CabDealSchema(many=False).dump(data)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        deal = CabDeal.query.filter_by(id=id).first()
        if not deal:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        CabDealAssociation.query.filter_by(deal_id=id).delete()
        CabDeal.delete_db(deal)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/images', methods=['GET', 'POST'])
def cab_image_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        data = CabImage.query.filter_by(**args).offset((page - 1) * per_page).limit(per_page).all()
        result = CabImageSchema(many=True).dump(data)
        return jsonify({'result': {'images': result.data}, 'message': "Success", 'error': False})
    else:
        post = CabImage(**request.json)
        post.save()
        result = CabImageSchema().dump(post)
        return jsonify({'result': {'image': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/image/<int:id>', methods=['PUT', 'DELETE'])
def cab_image_id(id):
    if request.method == 'PUT':
        put = CabImage.query.filter_by(id=id).update(request.json)
        if put:
            CabImage.update_db()
            s = CabImage.query.filter_by(id=id).first()
            result = CabImageSchema(many=False).dump(s)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        cab_images = CabImage.query.filter_by(id=id).first()
        if not cab_images:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        CabImage.delete_db(cab_images)
        return jsonify({'result': {}, 'message': "Success", 'error': False})

@app.route('/api/v1/cab/website', methods=['GET', 'POST'])
def cabWebsite_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        web = CabWebsite.query.filter_by(**args).all()
        result = CabWebsiteSchema(many=True).dump(web)
        return jsonify({'result': {'website': result.data}, 'message': "Success", 'error': False})
    else:
        post = CabWebsite(**request.json)
        post.save()
        result = CabWebsiteSchema().dump(post)
        return jsonify({'result': {'website': result.data}, 'message': "Success", 'error': False})



@app.route('/api/v1/cab/booking', methods=['GET', 'POST'])
def cab_booking():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        data = CabBooking.query.filter_by(**args).offset((page - 1) * per_page).limit(per_page).all()
        result = CabBookingSchema(many=True).dump(data)
        return jsonify({'result': {'bookings': result.data}, 'message': "Success", 'error': False})
    else:
        booking = request.json
        tax = booking.get("tax", None)
        user = booking.get("user", None)
        booking.pop('user', None)
        booking.pop('tax', None)
        tax_post = CabTax(**tax)
        tax_post.save()
        user_post = CabUser(**user)
        user_post.save()
        booking["tax_id"] = tax_post.id
        booking["user_id"] = user_post.id
        booking_post = CabBooking(**booking)
        booking_post.save()
        booking_post.tax = tax_post
        booking_post.user = user_post
        result = CabBookingSchema().dump(booking_post)
        return jsonify({'result': {'bookings': result.data}, 'message': "Success", 'error': False})

@app.route('/api/v1/cab/booking/<int:id>', methods=['PUT', 'DELETE'])
def cab_booking_id(id):
    if request.method == 'PUT':
        put = CabBooking.query.filter_by(id=id).update(request.json)
        if put:
            CabBooking.update_db()
            data = CabBooking.query.filter_by(id=id).first()
            result = CabBookingSchema(many=False).dump(data)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        booking = CabBooking.query.filter_by(id=id).first()
        if not booking:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        CabTax.query.filter_by(booking_id=id).delete()
        CabBooking.delete_db(booking)
        return jsonify({'result': {}, 'message': "Success", 'error': False})



@app.route('/api/v1/cab/tax', methods=['GET', 'POST'])
def cab_tax():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        data = CabTax.query.filter_by(**args).offset((page - 1) * per_page).limit(per_page).all()
        result = CabTaxSchema(many=True).dump(data)
        return jsonify({'result': {'taxes': result.data}, 'message': "Success", 'error': False})
    else:
        post = CabTax(**request.json)
        post.save()
        result = CabTaxSchema().dump(post)
        return jsonify({'result': {'taxes': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/website', methods=['GET', 'POST'])
def cab_website_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        web = CabWebsite.query.filter_by(**args).all()
        result = CabWebsiteSchema(many=True).dump(web)
        return jsonify({'result': {'website': result.data}, 'message': "Success", 'error': False})
    else:
        post = CabWebsite(**request.json)
        post.save()
        result = CabWebsiteSchema().dump(post)
        return jsonify({'result': {'website': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/collection', methods=['GET', 'POST'])
def cab_collection_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        args.pop('page', None)
        args.pop('per_page', None)
        data = CabCollection.query.filter_by(**args).all()
        result = CabCollectionSchema(many=True).dump(data)
        return jsonify({'result': {'collection': result.data}, 'message': "Success", 'error': False})
    else:
        collection = request.json
        products = collection.get("products", None)
        collection.pop('products', None)
        collection_post = CabCollection(**collection)
        collection_post.save()
        for product in products:
            product_post = CabCollection(**product)
            collection_post.products.appand(product_post)
            product_post.save()
        result = CabCollectionSchema().dump(collection_post)
        return jsonify({'result': {'collection': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/collection/<int:id>', methods=['PUT', 'DELETE'])
def cab_collection_id(id):
    if request.method == 'PUT':
        put = CabCollection.query.filter_by(id=id).update(request.json)
        if put:
            CabCollection.update_db()
            s = CabCollection.query.filter_by(id=id).first()
            result = CabCollectionSchema(many=False).dump(s)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        collection = CabCollection.query.filter_by(id=id).first()
        if not collection:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        else:
            CabCollectionProduct.query.filter_by(cab_collection_id=collection.id).delete()
            CabCollection.delete_db(collection)
        return jsonify({'result': {}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/collection/product', methods=['GET', 'POST'])
def cab_collection_product_api():
    if request.method == 'GET':
        args = request.args.to_dict()
        data = CabCollectionProduct.query.filter_by(**args).all()
        result = CabCollectionProductSchema(many=True).dump(data)
        return jsonify({'result': {'products': result.data}, 'message': "Success", 'error': False})
    else:
        post = CabCollectionProduct(**request.json)
        post.save()
        result = CabCollectionProductSchema().dump(post)
        return jsonify({'result': {'products': result.data}, 'message': "Success", 'error': False})


@app.route('/api/v1/cab/collection/product/<int:id>', methods=['PUT', 'DELETE'])
def cab_product_id(id):
    if request.method == 'PUT':
        put = CabCollectionProduct.query.filter_by(id=id).update(request.json)
        if put:
            CabCollectionProduct.update_db()
            s = CabCollectionProduct.query.filter_by(id=id).first()
            result = CabCollectionProductSchema(many=False).dump(s)
            return jsonify({'result': result.data, "status": "Success", 'error': False})
    else:
        collection_product = CabCollectionProduct.query.filter_by(id=id).first()
        if not collection_product:
            return jsonify({'result': {}, 'message': "No Found", 'error': True})
        CabCollectionProduct.delete_db(collection_product)
        return jsonify({'result': {}, 'message': "Success", 'error': False})
