# cripto-history-data
Cripto assets history prices data from various exchanges

Binance Klines Headers

Open time,Open,High,Low,Close,Volume,Close time,Quote asset volume,Number of trades,Taker buy base asset volume,Taker buy quote asset volume,Ignore

### Run in container

docker run --rm -it -v ${PWD}:/var/code --name=cripto-history-data cripto-history-data /bin/sh

### URL and payload for request
curl 'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/spot/daily/klines/LTCUSDC/12h/' \
  -H 'Accept: */*' \
  -H 'Accept-Language: en-US,en;q=0.9,pt;q=0.8' \
  -H 'Cache-Control: no-cache' \
  -H 'Connection: keep-alive' \
  -H 'Origin: https://data.binance.vision' \
  -H 'Pragma: no-cache' \
  -H 'Referer: https://data.binance.vision/' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Site: cross-site' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36' \
  -H 'sec-ch-ua: "Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  --compressed --output=./test.txt

If you are considering donate to the work these are the addresses

Bitcoin: 1EUGcJHS49242UpDXNVoLVzWSTVPRKmRth
Litecoin: LbqRSz5i225FqED4QTFwjU5qQS72cRdvoe
Ripple XRP: 