# These targets are not files
.PHONY: install sandbox geoip demo docs coverage lint travis messages compiledmessages css clean preflight make_sandbox make_demo

install:
	pip install -e . -r requirements.txt

build_sandbox:
	# Remove media
	-rm -rf sandbox/public/media/images
	-rm -rf sandbox/public/media/cache
	-rm -rf sandbox/public/static
	-rm -f sandbox/db.sqlite
	# Create database
	sandbox/manage.py migrate
	# Import some fixtures. Order is important as JSON fixtures include primary keys
	sandbox/manage.py loaddata sandbox/fixtures/child_products.json
	sandbox/manage.py oscar_import_catalogue sandbox/fixtures/*.csv
	sandbox/manage.py oscar_import_catalogue_images sandbox/fixtures/images.tar.gz
	sandbox/manage.py oscar_populate_countries
	sandbox/manage.py loaddata _fixtures/pages.json _fixtures/auth.json _fixtures/ranges.json _fixtures/offers.json
#	sandbox/manage.py loaddata sandbox/fixtures/orders.json
	sandbox/manage.py clear_index --noinput
	sandbox/manage.py update_index catalogue

sandbox: install build_sandbox

geoip:
	wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
	gunzip GeoLiteCity.dat.gz
	mv GeoLiteCity.dat demo/geoip

docs:
	cd docs && make html

todo:
	# Look for areas of the code that need updating when some event has taken place (like 
	# Oscar dropping support for a Django version)
	-grep -rnH TODO *.txt
	-grep -rnH TODO worldpay
	-grep -rnH "django.VERSION" worldpay
