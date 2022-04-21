import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="", db="scrapy_spider", charset="utf8")
cursor = conn.cursor()


def crawl_ips():
    # crawl ip proxies
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0"}
    for i in range(1):
        response = requests.get("https://ip.jiangxianli.com/?page=1&country=%E4%B8%AD%E5%9B%BD", headers=headers)
        selector = Selector(text=response.text)
        all_trs = selector.css("tbody > tr")
        ip_list = []

        def parse_delay(delay):
            if (delay.find("秒") and delay.find("毫秒") == -1):
                return int((float(delay.replace("秒", ""))) * 1000)
            elif delay.find("毫秒"):
                return (int(delay.replace("毫秒", "")))

        for tr in all_trs[0:]:
            all_texts = tr.css("td::text").extract()
            if (len(all_texts) == 0):
                continue
            ip = all_texts[0]
            port = all_texts[1]
            protocol = all_texts[3]
            region = all_texts[4]
            nation = all_texts[5]
            delay = parse_delay(all_texts[7])
            ip_list.append({
                "ip": ip,
                "port": port,
                "protocol": protocol,
                "region": region,
                "nation": nation,
                "delay": delay
            })

        for ip_info in ip_list:
            sql = "INSERT INTO proxy_ip (ip, port, protocol, region, nation, delay) VALUES(%s, %s, %s, %s, %s, %s)"
            params = (ip_info["ip"], ip_info["port"], ip_info["protocol"], ip_info["region"], ip_info["nation"], ip_info["delay"])
            cursor.execute(sql, params)
            conn.commit()

class GetIP(object):
    def delete_ip(self, ip):
        # delete deprecated ips
        delete_sql = "delete from proxy_ip where ip = '{0}'".format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True

    def judge_ip(self, ip, port):
        # is this ip valid ?
        http_url = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        try:
            proxy_dict = {
                "http": proxy_url,
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print ("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print ("effective ip")
                return True
            else:
                print  ("invalid ip and port")
                self.delete_ip(ip)
                return False


    def get_random_ip(self):
        # get an ip randomly from database
        random_sql = "SELECT ip, port FROM proxy_ip ORDER BY RAND() LIMIT 1"
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            judge_result = self.judge_ip(ip, port)
            if judge_result:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()

if __name__ == "__main__":
    get_ip = GetIP()
    print(get_ip.get_random_ip())