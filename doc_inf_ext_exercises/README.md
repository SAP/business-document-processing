# Exercise 2 - Document Information Extraction

In this exercise, we will use Document Information Extraction Service to do following:

- Upload documents for extraction using UI.
- Correct and confirm extracted information using UI.
- Retrieve extracted information using REST API.
- Upload supplier Master Data for invoices.
- Upload document for extraction using REST API and enable enrichments for matching supplier id with Sender information.

## Exercise 2.1 - Set up Document Information Extraction Service and UI

After completing below step you will have access for Document Information Extraction Service and its UI Application

1. Follow this [tutorial](https://developers.sap.com/tutorials/cp-aibus-dox-booster-app.html) to create instance of Document Information Extraction Service and Subscribe to UI.

Now that we have access to UI Application, we'll goto the UI Application for our next exercise.
**Make sure you also download the service key, since we'll be using it in subsequent exercises.**

## Exercise 2.2 - Upload documents for Extraction using UI Application

Following step will guide you on how to use Document Information Extraction Service UI to extract information from Invoices and Payment Advices.

**Please make sure you have downloaded the [data.zip](/data.zip) folder which contains the test documents and unziped it**

1.	In the top right, click + (Upload a new document) and choose all the pdf documents in [data/invoice](/data/Invoice) folder
   <br>![](/exercises/ex2/images/02_02_1.png)

2.	In the Select Document screen, drop Invoice files directly or click + to upload one or more document files.
   <br>![](/exercises/ex2/images/02_02_2.png)

3. Select the Document Type **Invoice**. 
   <br>![](/exercises/ex2/images/02_02_3.png)

4. Click **Step 2** button.
   <br>![](/exercises/ex2/images/02_02_4.png)

5. In Step 2, select the **Header Fields** you want to extract from the invoice documents. We'll be extracting following header fields from invoice documents.
   - Invoice Number
   - Invoice Date
   - Purchase Order Number
   - Net Amount
   - Gross Amount
   - Tax Amount
   - Currency
   - Buyer Name
   - Buyer Address
   - Payment Terms
   - Supplier Bank Account
   - Supplier Name
   - Supplier Address

   Click **Step 3** button.
   <br>![](/exercises/ex2/images/02_02_5.png)

6. In Step 3, select the **Line Items Fields** you want to extract from the invoice documents. We'll be extracting following line items fields from invoice documents.
   - Description
   - Amount
   - Quantity
   - Unit Price

   Click **Review** button.
   <br>![](/exercises/ex2/images/02_02_6.png)

7. Review your selection. Click **Confirm** button.
   <br>![](/exercises/ex2/images/02_02_7.png)

8. You'll see the Document Name, Upload Date and Status of the documents you have just uploaded.
   <br>![](/exercises/ex2/images/02_02_8.png)
   Status changes from PENDING to READY. This means the selected header fields and line items have been extracted, and the extraction results are ready to be validated and changed if necessary. If status changes from PENDING to FAILED, this means it was not possible to get the extraction results, and you need to upload the document once again.
   <br>![](/exercises/ex2/images/02_02_9.png)

9. *[Try this later] Repeat above steps 1-7 for Payment Advice Documents. Only difference is, in Step 3 Select Document Type **Payment Advices** and select header fields and line items relevant for Payment Advice documents.*

Now that you have uploaded document for extraction in the next section we'll see the extraction results on UI Application.


## Exercise 2.3 - Visualize, Correct Extraction Results and Confirm Document using UI Application

Following Steps will guide to use UI Application for viewing and correcting extraction results of document and mark it as Confirmed.

1. Click on **twitter.pdf (Invoice)** in the Documents list to open the Preview if the document.

2. Click on the **Extraction Results** Button to view the extracted information.
   <br>![](/exercises/ex2/images/02_03_2.png)

3. Check the extracted Header Fields and Line Items.
   <br>![](/exercises/ex2/images/02_03_3.png)

4. Click on input field label **Supplier Bank Account** to highlight location from where the value is extracted from in Preview.
   <br>![](/exercises/ex2/images/02_03_4.png)

5. Expand First Line Item and click on **Description** to to highlight location from where the value is extracted from in Preview.
   <br>![](/exercises/ex2/images/02_03_5.png)

6. Click on **Edit** Button, to fix some wrongly extracted information.
   <br>![](/exercises/ex2/images/02_03_6.png)

7. Click on Currency Code Input Field, Search for **British** in Currencies Dialog Box and Click on **British Pound**.
   <br>![](/exercises/ex2/images/02_03_7.png)

8. Draw a selection box around **Due Date: 31/2/2018** in Document Preview, select **Payement Terms** for field in **Assign Field** Popover and click **Apply**.
   <br>![](/exercises/ex2/images/02_03_8.gif)

9. Now that all the information is correct, Click on **Confirm** button and then again click **Confirm** button in the **Confirm Extracted Values?** dialog box to save the information and mark the results as **Confirmed**.
   <br>![](/exercises/ex2/images/02_03_9.png)

You'll notice that the document status has change to **CONFIRMED**.
<br>![](/exercises/ex2/images/02_03_10.png)

NOTE: A document that is **CONFIRMED** indicates that the results are reviewed and corrected(if needed) by a User.

Now that you've marked **twitter.pdf** as CONFIRMED it means that values of Header Fields and Line Items are correct as per the content of Document. In the upcoming sections we'll try access these values through the Rest API.

## Exercise 2.4 - Get Auth Token to use Document Information Extraction Rest API

In order to use the Rest API of Document Information Extraction we'll need the Auth Token.

Here we'll will need the service key that you downloaded in Exercise 2.1.

Follow this [tutorial](https://developers.sap.com/tutorials/cp-aibus-dox-web-oauth-token.html) to get the Auth Token.

NOTE: Keep the tab open since we'll need access token in next steps

## Exercise 2.5 - Get Extraction Results of Document using Rest API

You will use Swagger UI, via any web browser, to call the Document Information Extraction Rest APIs. Swagger UI allows developers to effortlessly interact and try out every single operation an API exposes for easy consumption. For more information, see [Swagger UI](https://swagger.io/tools/swagger-ui/).

In the service key you downloaded for Document Information Extraction in Exercise 2.1, you should find (outside the uaa section of the service key) an entry called url and another entry called swagger (as highlighted in the image below).

1. To access the Document Information Extraction Swagger UI, add the swagger value (**/document-information-extraction/v1**) to the url value, paste it in any web browser and press Enter.
   <br>![](/exercises/ex2/images/02_05_1.png)

2. To be able to use the Swagger UI endpoints you need to authorize yourself. In the top right corner, click **Authorize**.
   <br>![](/exercises/ex2/images/02_05_2.png)

3. Get the access_token value created in the previous exercise: Get Auth Token to use Document Information Extraction Rest API, then add **bearer** in front of it, and enter in the **Value** field. eg. `bearer <access_token>`
   <br>![](/exercises/ex2/images/02_05_3.png)

4. Click **Authorize**, and then click **Close**.
   <br>![](/exercises/ex2/images/02_05_4.png)

5. Expand the **GET /document/jobs** endpoint and click **Try it Out**.
   <br>![](/exercises/ex2/images/02_05_5.png)

6. Input value `default` in **clientId** parameter and click on **Execute**.
   <br>![](/exercises/ex2/images/02_05_6.png)

7. Check the **Response Body**, it will contain list of jobs in json format.
   <br>![](/exercises/ex2/images/02_05_7.png)

8. In the **Response Body**, find the document with `"status": "CONFIRMED"`, you'll find that this is the same **twitter.pdf** that we confirmed in Exercise 2.3.
   <br>![](/exercises/ex2/images/02_05_8.png)

9. Copy the value corresponding to `id` for **twitter.pdf**.
   <br>![](/exercises/ex2/images/02_05_9.png)

10. Collapse **GET /document/jobs** endpoint and Expand the **GET /document/jobs/{id}** endpoint.

11. Click **Try it Out**
   <br>![](/exercises/ex2/images/02_05_11.png)

12. Paste the value of `id` copied in step 9 into the **id** parameter and click on **Execute**.
   <br>![](/exercises/ex2/images/02_05_12.png)

13. Check the **Reponse Body**, you'll find the information about job like `filename`, `status` etc. `headerFields` contains extraction results of Header fields. `lineItems` will contains results for Line items.
   <br>![](/exercises/ex2/images/02_05_13a.png)
   <br>![](/exercises/ex2/images/02_05_13b.png)

Now, that you know how to retrive extracted value for a document you can consume these Rest API's in order to integrate with any other application.

Currently SAP products like Concur, S4 Payment Advice Management, IRPA, etc have integrated with the service using the API's.

## Exercise 2.6 - Upload Supplier Data for matching

One of the important features of Document Information Extraction Service is that it could match extraction information with relevent master data provided by the customers.

In order to achive this we need to Upload the master data into Service and this exercise will guide you to do so. 
We'll using Swagger UI to upload the master data via Rest API.

After completing below steps you will have Supplier master data uploaded to the Service which can be matched with the sender details of the invoice documents.

1. Expand the **POST /data/jobs** endpoint and click **Try it out**.
<br>![](/exercises/ex2/images/02_06_1.png)

2. Define the data in the payload field, so that the system knows which extracted field (using, for example, supplier IDs from master data) should be enriched. The date is below.
   ```json
   {
      "value":[
         {
            "id":"BE0001",
            "name":"Umbro LLC",
            "accountNumber":"",
            "address1":"15 Sports Goods Street, London UD12 3TY",
            "address2":"",
            "city":"",
            "countryCode":"",
            "postalCode":"",
            "state":"",
            "email":"",
            "phone":"",
            "bankAccount":"UK8080808080",
            "taxId":""
         },
         {
            "id":"BE0002",
            "name":"Twitter UK",
            "accountNumber":"",
            "address1":"15 Tweetdrive, Worthing BN12 3NX",
            "address2":"",
            "city":"",
            "countryCode":"",
            "postalCode":"",
            "state":"",
            "email":"",
            "phone":"",
            "bankAccount":"GB34 5654 33456 3456 4565 35",
            "taxId":""
         },
         {
            "id":"BE0003",
            "name":"RC Consulting LLC",
            "accountNumber":"",
            "address1":"15 Enterprise Lane, Boston, MA 02125",
            "address2":"",
            "city":"",
            "countryCode":"",
            "postalCode":"",
            "state":"",
            "email":"",
            "phone":"",
            "bankAccount":"US11 1111 1111 2222 33",
            "taxId":""
         },
         {
            "id":"BE0004",
            "name":"Norsk Folkehjelp",
            "accountNumber":"",
            "address1":"Stortorvet 100, 0255 OSLO Ministry of Health Aristotelous 17 Athina 104 33 Greece",
            "address2":"",
            "city":"",
            "countryCode":"",
            "postalCode":"",
            "state":"",
            "email":"",
            "phone":"",
            "bankAccount":"NO80 8080 8080 8080 80",
            "taxId":""
         },
         {
            "id":"BE0005",
            "name":"NSYFAC Naval Facilities Engineering Command",
            "accountNumber":"",
            "address1":"Military Base 15, D.C. 65472-8326 US Command",
            "address2":"",
            "city":"",
            "countryCode":"",
            "postalCode":"",
            "state":"",
            "email":"",
            "phone":"",
            "bankAccount":"US67 6767 6767 6767 6767 67",
            "taxId":""
         },
         {
            "id":"BE0006",
            "name":"Beijing 2008 OOC",
            "accountNumber":"",
            "address1":"15 Sports Goods Street, Bejing UD12 3TY",
            "address2":"",
            "city":"",
            "countryCode":"",
            "postalCode":"",
            "state":"",
            "email":"",
            "phone":"",
            "bankAccount":"CN80 8080 8080 8080 8080 80",
            "taxId":""
         },
         {
            "id":"BE0007",
            "name":"Chinese Blogger Conference",
            "accountNumber":"",
            "address1":"Soho Tower, 25 Hart Avenue, Hong Kong",
            "address2":"",
            "city":"",
            "countryCode":"",
            "postalCode":"",
            "state":"",
            "email":"",
            "phone":"",
            "bankAccount":"CN36 9369 3693 6936 9369 36",
            "taxId":""
         },
         {
            "id":"BE0008",
            "name":"Engenharia Ambiental",
            "accountNumber":"",
            "address1":"Service Drive 15, 18767 Manchester",
            "address2":"",
            "city":"",
            "countryCode":"",
            "postalCode":"",
            "state":"",
            "email":"",
            "phone":"",
            "bankAccount":"GB27 2789 2789 2789 2789 89",
            "taxId":""
         },
         {
            "id":"BE0009",
            "name":"Flickr",
            "accountNumber":"",
            "address1":"Entrepeneurweg 15, 54321 Neustadt",
            "address2":"",
            "city":"",
            "countryCode":"",
            "postalCode":"",
            "state":"",
            "email":"",
            "phone":"",
            "bankAccount":"DE28 4321 4321 4321 4321 21",
            "taxId":""
         },
         {
            "id":"BE0010",
            "name":"guru shop",
            "accountNumber":"",
            "address1":"Expertenweg 15, 90120 Gláubighausen",
            "address2":"",
            "city":"",
            "countryCode":"",
            "postalCode":"",
            "state":"",
            "email":"",
            "phone":"",
            "bankAccount":"DE12 3412 3412 3412 34",
            "taxId":""
         }
      ]
   }
   ```
   <br>![](/exercises/ex2/images/02_06_2.png)

3. Choose the enrichment data **type** value `businessEntity`.

4. Enter **clientId** as `default` .

5. Choose the **subtype** value `supplier`.

6. Click **Execute**.
   <br>![](/exercises/ex2/images/02_06_6.png)

7. You should receive a response like the following with status PENDING, copy the `id` from the Response body to see the result of the enrichment data status in the next step.
   <br>![](/exercises/ex2/images/02_06_7.png)

8. Expand the **GET /data/jobs/{id}** endpoint and click **Try it out**.
   <br>![](/exercises/ex2/images/02_06_8.png)

9. Paste the `id` copied in step 8, in `id` parameter and click **Execute**
   <br>![](/exercises/ex2/images/02_06_9.png)

10. You should receive a response like the following with status `SUCCESS`. If it's still `PENDING` try again in some time.
   <br>![](/exercises/ex2/images/02_06_10.png)

Now that you have uploaded the supplier data, we can use the service to find `id` of the Supplier that matches the extracted Supplier information for invoices.

## Exercise 2.7 - Upload Document through Rest API to enrich the Extraction results with Supplier Data

In order to predict the Master data based on Extraction Result, We need to add **enrichment** configuration when we upload the document for extraction. We can provide this configuration when we upload the document via Rest API.

NOTE: this configuration option is not avaible in the UI Application and is one of the planned to be avaible in future.

In this exercise we will again use Swagger UI to upload a Invoice document along with enrichment configuration via rest api for Extraction.

1. Expand the **POST /document/jobs** endpoint and click **Try it out**.
   <br>![](/exercises/ex2/images/02_07_1.png)

2. Choose one of the invoice document file you want to enrich for **file** parameter.
   <br>![](/exercises/ex2/images/02_07_2.png)

3. In **options**, you'll enter the list of header and line items fields to be extracted from the uploaded file, the **clientId** as `default`, the **documentType** as `invoice`, the enrichment configuration to match **Supplier** information with data **type** as `businessEntity` and **subtype** as `supplier`. The Payload will be as following:
   ```json
   {
      "extraction":{
         "headerFields":[
            "documentNumber",
            "purchaseOrderNumber",
            "netAmount",
            "senderAddress",
            "senderName",
            "senderBankAccount",
            "grossAmount",
            "currencyCode",
            "documentDate",
            "taxAmount",
            "receiverName",
            "receiverAddress",
            "paymentTerms"
         ],
         "lineItemFields":[
            "description",
            "netAmount",
            "quantity",
            "unitPrice"
         ]
      },
      "clientId":"default",
      "documentType":"invoice",
      "enrichment":{
         "sender":{
            "top":1,
            "type":"businessEntity",
            "subtype":"supplier"
         }
      }
   }
   ```
   <br>![](/exercises/ex2/images/02_07_3.png)

4. Click **Execute**.

5. You'll get a response with **status** as `PENDING`. Copy the value of `id` in response payload.
   <br>![](/exercises/ex2/images/02_07_5.png)

6. Expand the **GET /document/jobs/{id}** endpoint, and click **Try it out**.
   <br>![](/exercises/ex2/images/02_07_6.png)

7. Paste the id copied in step 5 as the **id** in parameter. click on **Execute**.
   <br>![](/exercises/ex2/images/02_07_7.png)

8. Check the response body, if the status is **DONE**, within `extractions.headerFields` one of the extracted fields is `senderName` with value `Twitter UK,`. Within `enrichtment.sender` you'll see the supplier ID predictions from master data uploaded in **excersice 2.6**. The prediction suggests supplier ID `BE0002` which corresponds to `Twitter UK`.
   <br>![](/exercises/ex2/images/02_07_8.png)

Now that you know how to enrich extraction results with master data, you can use this matching provided by Document Information Service to automatically link the Extracted Information with Suppliers.

## Summary

You've now completed the Exercise and learned 
- How to consume Document Information Extraction Service using Rest API.
- How to visualize and validated extraction results using the UI Application.

Useful Links 
- [Tutorials](https://developers.sap.com/tutorial-navigator.html?tag=products:technology-platform/sap-ai-business-services/document-information-extraction) for Document Information Extraction
- [Help Page](https://help.sap.com/viewer/product/DOCUMENT_INFORMATION_EXTRACTION) for Document Information Extraction

