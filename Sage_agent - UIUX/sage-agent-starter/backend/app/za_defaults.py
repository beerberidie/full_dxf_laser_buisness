"""
South African Business Defaults for Sage Business Cloud Accounting

Provides default values and configurations specific to South African businesses.
"""

from typing import Dict, Any
from decimal import Decimal


# South African Currency
ZA_CURRENCY = "ZAR"
ZA_CURRENCY_SYMBOL = "R"

# South African VAT Rate (Standard Rate)
ZA_VAT_RATE = Decimal("15.00")  # 15% VAT
ZA_VAT_CODE = "ZA_STANDARD"

# Payment Terms
ZA_DEFAULT_PAYMENT_TERMS_DAYS = 30
ZA_PAYMENT_TERMS_OPTIONS = {
    "immediate": 0,
    "7_days": 7,
    "14_days": 14,
    "30_days": 30,
    "60_days": 60,
    "90_days": 90,
}

# Region Code
ZA_REGION_CODE = "ZA"
ZA_COUNTRY_NAME = "South Africa"

# Date Format
ZA_DATE_FORMAT = "%Y-%m-%d"  # ISO 8601 format
ZA_DISPLAY_DATE_FORMAT = "%d/%m/%Y"  # Display format: DD/MM/YYYY

# Number Formatting
ZA_DECIMAL_SEPARATOR = "."
ZA_THOUSANDS_SEPARATOR = ","
ZA_DECIMAL_PLACES = 2

# Business Hours (South African Standard Time - SAST, UTC+2)
ZA_TIMEZONE = "Africa/Johannesburg"
ZA_BUSINESS_HOURS_START = "08:00"
ZA_BUSINESS_HOURS_END = "17:00"


class ZADefaults:
    """
    South African business defaults configuration.
    """
    
    @staticmethod
    def get_default_currency() -> str:
        """Get default currency code for South Africa."""
        return ZA_CURRENCY
    
    @staticmethod
    def get_vat_rate() -> Decimal:
        """Get standard VAT rate for South Africa."""
        return ZA_VAT_RATE
    
    @staticmethod
    def get_vat_code() -> str:
        """Get VAT code for Sage API."""
        return ZA_VAT_CODE
    
    @staticmethod
    def get_default_payment_terms() -> int:
        """Get default payment terms in days."""
        return ZA_DEFAULT_PAYMENT_TERMS_DAYS
    
    @staticmethod
    def get_region_code() -> str:
        """Get region code for South Africa."""
        return ZA_REGION_CODE
    
    @staticmethod
    def get_invoice_defaults() -> Dict[str, Any]:
        """
        Get default values for creating invoices.
        
        Returns:
            Dictionary with default invoice values
        """
        return {
            "currency": ZA_CURRENCY,
            "payment_terms_days": ZA_DEFAULT_PAYMENT_TERMS_DAYS,
            "vat_rate": float(ZA_VAT_RATE),
            "region": ZA_REGION_CODE,
        }
    
    @staticmethod
    def get_quote_defaults() -> Dict[str, Any]:
        """
        Get default values for creating quotes.
        
        Returns:
            Dictionary with default quote values
        """
        return {
            "currency": ZA_CURRENCY,
            "validity_days": 30,  # Quotes valid for 30 days
            "vat_rate": float(ZA_VAT_RATE),
            "region": ZA_REGION_CODE,
        }
    
    @staticmethod
    def get_contact_defaults() -> Dict[str, Any]:
        """
        Get default values for creating contacts.
        
        Returns:
            Dictionary with default contact values
        """
        return {
            "country": ZA_COUNTRY_NAME,
            "region": ZA_REGION_CODE,
            "currency": ZA_CURRENCY,
            "payment_terms_days": ZA_DEFAULT_PAYMENT_TERMS_DAYS,
        }
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """
        Format amount as South African currency.
        
        Args:
            amount: Numeric amount
            
        Returns:
            Formatted currency string (e.g., "R 1,234.56")
        """
        formatted = f"{amount:,.{ZA_DECIMAL_PLACES}f}"
        return f"{ZA_CURRENCY_SYMBOL} {formatted}"
    
    @staticmethod
    def calculate_vat(net_amount: float) -> float:
        """
        Calculate VAT amount from net amount.
        
        Args:
            net_amount: Net amount before VAT
            
        Returns:
            VAT amount
        """
        return round(net_amount * float(ZA_VAT_RATE) / 100, ZA_DECIMAL_PLACES)
    
    @staticmethod
    def calculate_total_with_vat(net_amount: float) -> float:
        """
        Calculate total amount including VAT.
        
        Args:
            net_amount: Net amount before VAT
            
        Returns:
            Total amount including VAT
        """
        vat = ZADefaults.calculate_vat(net_amount)
        return round(net_amount + vat, ZA_DECIMAL_PLACES)
    
    @staticmethod
    def get_workspace_defaults() -> Dict[str, Any]:
        """
        Get complete workspace defaults for South African business.
        This is used to initialize workspace settings.
        
        Returns:
            Dictionary with all workspace defaults
        """
        return {
            "region": ZA_REGION_CODE,
            "country": ZA_COUNTRY_NAME,
            "currency": ZA_CURRENCY,
            "currency_symbol": ZA_CURRENCY_SYMBOL,
            "vat_rate": float(ZA_VAT_RATE),
            "vat_code": ZA_VAT_CODE,
            "payment_terms_days": ZA_DEFAULT_PAYMENT_TERMS_DAYS,
            "timezone": ZA_TIMEZONE,
            "date_format": ZA_DATE_FORMAT,
            "display_date_format": ZA_DISPLAY_DATE_FORMAT,
            "decimal_separator": ZA_DECIMAL_SEPARATOR,
            "thousands_separator": ZA_THOUSANDS_SEPARATOR,
            "decimal_places": ZA_DECIMAL_PLACES,
        }


# Singleton instance
za_defaults = ZADefaults()


def get_za_defaults() -> ZADefaults:
    """
    Get South African defaults instance.
    
    Returns:
        ZADefaults instance
    """
    return za_defaults

