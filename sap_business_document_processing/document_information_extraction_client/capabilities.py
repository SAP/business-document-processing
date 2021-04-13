# SPDX-FileCopyrightText: 2020 2019-2020 SAP SE
#
# SPDX-License-Identifier: Apache-2.0

from enum import Enum


DOCUMENT_TYPE_ADVICE = "paymentAdvice"
DOCUMENT_TYPE_INVOICE = "invoice"
DATA_TYPE_BUSINESS_ENTITY = "businessEntity"
DATA_TYPE_EMPLOYEE = "employee"
DATA_SUBTYPE_COMPANYCODE = "companyCode"
DATA_SUBTYPE_CUSTOMER = "customer"
DATA_SUBTYPE_SUPPLIER = "supplier"


class DoxDataType(Enum):
    EMPLOYEE = DATA_TYPE_EMPLOYEE
    BUSINESS_ENTITY = DATA_TYPE_BUSINESS_ENTITY

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return other.value == self.value
        if type(other) is str:
            return other == self.value
        raise NotImplementedError

    def __str__(self):
        return self.value


class DoxDataSubType(Enum):
    SUPPLIER = DATA_SUBTYPE_SUPPLIER
    CUSTOMER = DATA_SUBTYPE_CUSTOMER
    COMPANY_CODE = DATA_SUBTYPE_COMPANYCODE

    def __str__(self):
        return self.value


HEADER_FIELD_NAMES_FOR_DOCUMENT_TYPES = {
    DOCUMENT_TYPE_INVOICE: ["documentNumber", "taxId", "taxName", "purchaseOrderNumber", "shippingAmount", "netAmount",
                            "grossAmount", "currencyCode", "receiverContact", "documentDate", "taxAmount", "taxRate",
                            "receiverName", "receiverAddress", "deliveryDate", "paymentTerms", "deliveryNoteNumber",
                            "senderBankAccount", "barcode", "senderAddress", "senderName"],
    DOCUMENT_TYPE_ADVICE: ["documentNumber", "grossAmount", "currencyCode", "documentDate", "senderName"]
}
LINE_ITEM_FIELDS_NAMES_FOR_DOCUMENT_TYPES = {
    DOCUMENT_TYPE_INVOICE: ["description", "netAmount", "quantity", "unitPrice", "materialNumber"],
    DOCUMENT_TYPE_ADVICE: ["netAmount", "documentNumber", "documentDate", "discountAmount", "deductionAmount"],
}
