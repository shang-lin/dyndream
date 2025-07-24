Dyndream is a program that manages dynamic DNS for users with a Dreamhost account.

Dyndream uses Dreamhost's API to update a DNS record with your dynamic IP address.
To use Dyndream, you need a Dreamhost account, a key for the Dreamhost API, a remote web
endpoint that returns your IP address in JSON format, and a computer where you can run
dyndream.py. I run dyndream.py hourly through a cron job on my Raspberry Pi.

Blog post: [https://shang-lin.com/blog/2017/03/16/Dynamic-DNS-with-Dreamhost](https://shang-lin.com/blog/2017/03/16/Dynamic-DNS-with-Dreamhost)
