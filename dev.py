
import myModuleAWS
import boto3
import json


myModuleAWS.readCredentials()

URL_cola_hacia_back = "https://sqs.us-east-1.amazonaws.com/621668821568/ColaHaciaBack.fifo"
URL_cola_hacia_front = "https://sqs.us-east-1.amazonaws.com/621668821568/ColaHaciaFront.fifo"

sqs = boto3.client('sqs')
sqs.purge_queue(QueueUrl=URL_cola_hacia_front)
sqs.purge_queue(QueueUrl=URL_cola_hacia_back)









# ----------------------
# myModuleAWS.creatTable()



# # Example usage
# concert_name = "PinkFloyd"
# tickets_to_buy = 71

# updated_item = myModuleAWS.buy_concert_tickets(concert_name, tickets_to_buy)







# concert_name = "PinkFloyd"
# new_remaining_tickets = 80
# current_remaining_tickets = 100

# updated_item = myModuleAWS.update_concert_tickets(concert_name, new_remaining_tickets, current_remaining_tickets)

# if updated_item is not None:
#     print(f"Successfully updated {concert_name} tickets.")




# myModuleAWS.generarPDF("ticket.pdf", "Fran", "Pink Floyd", "3")

# myModuleAWS.subirDataBucket(nombre_bucket, "ticket.pdf")

# myModuleAWS.accederBucket(nombre_bucket, 'ticket.pdf', 'ticket_descargado.pdf')

# url_ticket = myModuleAWS.getURL(nombre_bucket, 'ticket.pdf', 3600)

# print(url_ticket)

# myModuleAWS.eliminarBucket(nombre_bucket)


