# -*- coding: utf-8 -*-
import scrapy

from lxml.etree import HTML
import json
from math import ceil

company_f = open('company1.txt', 'w', encoding='utf-8')
jobs_f = open('job1.txt', 'w', encoding='utf-8')
companyid_f = open('companyid1.txt', 'w', encoding='utf-8')


class CompanySpider(scrapy.Spider):
    name = 'company'
    allowed_domains = ['51job.com']
    # 目标网站
    start_urls = ['https://jobs.51job.com/all/co{}.html'.format(i) for i in range(1, 101)]

    def getCompany(self, selector):
        xpaths = [('//*[@id="hidCOID"]/@value', 'c_id'),
                  ('/html/body/div[2]/div[2]/div[2]/div/h1/@title', 'c_name'),
                  ('/html/body/div[2]/div[2]/div[2]/div/img/@src', 'c_logo'),
                  ('/html/body/div[2]/div[2]/div[2]/div/p/@title', 'c_type'),
                  ('/html/body/div[2]/div[2]/div[3]/div[1]/div/div/div[1]/div/text()', 'c_describtion'),
                  ('/html/body/div[2]/div[2]/div[3]/div[2]/div/p[1]/text()', 'c_address'),
                  ('/html/body/div[2]/div[2]/div[3]/div[2]/div/p[2]/span[2]/text()', 'c_website'),
                  ('//*[@id="hidTotal"]/@value', 'c_jobcount')]
        companyj = {}
        for x, key in xpaths:
            try:
                if key == 'c_describtion':
                    companyj[key] = selector.xpath(x)[0]
                elif key == 'c_address':
                    companyj[key] = selector.xpath(x)[1]
                else:
                    companyj[key] = selector.xpath(x)[0]
            except Exception as err:
                print(err.args)
                companyj[key] = '-'
        return companyj

    def getjobs(self, selector, c_id, prefix='//*[@id="joblistdata"]'):
        jobs = []
        try:
            jlen = len(selector.xpath(prefix + '//div[.]/p/a/@title'))
            for i in range(1, jlen + 1):
                jobstr = selector.xpath(prefix + '//div[{}]'.format(i))[0].xpath('string(.)')
                #     print(jobstr)
                jobhref = selector.xpath(prefix + '//div[{}]/p/a/@href'.format(i))[0]
                jobid = jobhref.split('/')[-1].split('.html')[0]
                job = jobstr.split('\r\n')[1:]
                #     print(job)
                jobj = {'j_id': jobid,
                        'c_id': c_id,
                        'j_name': job[0].replace(' ', ''),
                        'j_work_expe': job[1].replace(' ', ''),
                        'j_address': job[2].replace(' ', ''),
                        'j_salary': job[3].replace(' ', ''),
                        'j_pub_date': job[4].replace(' ', '')}
                jobs.append(jobj)
            return jobs
        except Exception as err:
            print(err.args, '没有招聘信息')
        return jobs

    '''解析下一页数据'''

    def nextJob(self, response):
        selector = HTML(response.text)
        '''提取岗位数据（pageno_1）'''
        c_id = response.url.split('/co')[-1].replace('.html', '')
        jobs = self.getjobs(selector, c_id, prefix='')
        for job in jobs:
            jobstr = json.dumps(job, ensure_ascii=False) + '\n'
            jobs_f.write(jobstr)
        print(len(jobs))

    def parse(self, response):
        selector = HTML(response.text)
        '''提取公司数据'''
        company = self.getCompany(selector)  # 字典数据=>字符串
        companystr = json.dumps(company, ensure_ascii=False) + '\n'
        print(companystr)
        # 保存到txt文本中
        company_f.write(companystr)
        companyid_f.write(company['c_id'] + '\n')
        '''提取岗位数据（pageno_1）'''
        jobs = self.getjobs(selector, company['c_id'])
        for job in jobs:
            jobstr = json.dumps(job, ensure_ascii=False) + '\n'
            jobs_f.write(jobstr)
            # print(jobstr)
        print(len(jobs))

        '''提取分页岗位数据'''
        url = response.url
        totalPage = ceil(int(company['c_jobcount']) / 20)
        for pageno in range(2, totalPage + 1):
            formdata = {'pageno': str(pageno), 'hidTotal': str(company['c_jobcount']), 'type': '', 'code': ''}
            yield scrapy.FormRequest(url, formdata=formdata, callback=self.nextJob)
