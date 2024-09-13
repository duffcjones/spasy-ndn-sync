import geohash

def main():
    
    geocode = 'dpwhwt'
    latitude, longitude = geohash.decode(geocode)
    print(f'{latitude}, {longitude}')


if __name__ == '__main__':
    print('Testing Geohashing...')
    main()