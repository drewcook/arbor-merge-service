# Environment

Please set the following environment variables:

- `NFT_STORAGE_API = <nft.storage api key>`

# To run server

uvicorn run server.main:app

# Example merge request
## GET /merge

`curl -X POST http://localhost:8000/merge -H "Content-Type: application/json" -d '{"sample_cids": ["bafybeifsdxxztl5jtgh7doue3ytqpv5yurren2lkeq6rdxaigjc22haevi", "bafybeigfocxfmpne6n4f2adls7ejlighfrz2t6fjtd7xebxnexnwyilf3m"]}' `
