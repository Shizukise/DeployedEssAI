import fitz

class Validations:

    """
    All validations methods to be called when validating a "Validation" should be defined in this class
    """

    def VEIvalidation(self,filepath):
        """
        Validation for VEI (enterprise specific) PDF should not have more than one "Vous etes ici" element
        We initialize it to return false, and if only one instance of V.E.I is found, we return true after 
        closing the document.
        """
        valid = False
        doc = fitz.open(filepath)
        for page_num in range(len(doc)):
            page = doc[page_num]
            text_instances = page.search_for("VOUS ETES ICI")   #Unit test should check if return value is multiple than 3 or not brainstorm here
            """
            search_for() method splits the string ["VOUS","ETES","ICI"]
            Hence the if block checking for len(3)
            """
            if len(text_instances) == 0:
                break
            if len(text_instances) == 3:
                valid = True
                doc.close()
                return valid
        for page_num in range(len(doc)):
            """
            Alternative in case user wrote vous etes ici in lowers"""
            page = doc[page_num]
            text_instances = page.search_for("vous etes ici")   
            if len(text_instances) == 0:
                break
            if len(text_instances) == 3:
                valid = True
                doc.close()
                return valid
        return valid
        