from django.shortcuts import render
from django.http import HttpResponse , JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

import braintree


gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="q6h74gbt27f7ngpf",
        public_key="cp47wg2krypr9zq4",
        private_key="bd6db33a3245bd2b9f5fe5e772650206"
    )
)


def validate_user_session(id,token):
    UserModel = get_user_model()

    try:
        user = UserModel.objects.get(pk = id)
        if user.session_token == token:
            return True
        return False
    except UserModel.DoesNotExist:
        return False


@csrf_exempt
def generate_token(request,id,token):
    if not validate_user_session(id,token):
        return JsonResponse({'error':'Invaild session! login again '})
    
    return JsonResponse({'clientToken':gateway.client_token.generate(),'success':True})

@csrf_exempt
def process_payment(request,id,token):
    if not validate_user_session(id,token):
        return JsonResponse({'error':'Invaild session! login again '})
    
    nonce_from_the_client = request.POST["paymentMethodNonce"]
    payment_from_the_client = request.POST["amount"]


    result = gateway.transaction.sale({
    "amount": payment_from_the_client,
    "payment_method_nonce": nonce_from_the_client,
    "options": {
      "submit_for_settlement": True
        }
    })
    if result.is_success:
        return JsonResponse({
            'success': result.is_success,
            'trasaction':{'id':result.transaction.id,'amount':result.transaction.amount} })
    else:
        return JsonResponse({'error':True,'success' : False})