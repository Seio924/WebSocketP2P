import socket
import threading
from queue import Queue
import random
import numpy as np

#클라이언트가 보내는 경우
#- 서버에게 자신의 행렬 보내기
#- 서버에게 연산 결과 보내기
def Send(client_sock, send_queue):
    
    while True:
        try:
            #새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            recv = send_queue.get()
            
            thread_num, type, pair = recv.split()

            if type == 'matrix':
                c_list = [1, 2, 3, 4]
                pair = list(map(int, pair.split(",")))
                complement = list(set(c_list) - set(pair)) #행렬을 받을 클라이언트 둘

                recv_client = random.choice(complement) #행렬을 받을 클라이언트 랜덤으로 선택

                pair_mul = pair[0] * pair[1]

                if int(thread_num) == min(pair):
                    #행렬의 가로
                    random_row = random.randint(0, 9) # 아무 행이나 선택
                    #msg = "matrix" + "행렬의 가로" + str(recv_client) + "row" + 가로의 번호
                    msg = "matrix" + str(pair_mul) + str(matrix[random_row]) + str(recv_client) + "row" + str(random_row) # 수정필요할지도
                    client_sock.send(bytes(msg.encode()))
                else:
                    #행렬의 세로
                    random_col = random.randint(0, 9) # 아무 열이나 선택
                    #msg = "matrix" + "행렬의 세로" + str(recv_client) + "col" + 세로의 번호
                    msg = "matrix" + str(pair_mul) + str(matrix[:, random_col]) + str(recv_client) + "col" + str(random_col) # 수정필요
                    client_sock.send(bytes(msg.encode()))
            
            elif type == 'calculating':
                pair_cal, data, rc, rc_num = pair.split()
                pair_check = []
                pair_check.append(pair_cal) # (수정) [[2], [해당 가로나 세로]] 로 저장하자
                if rc == "row": 
                    row = rc_num # (수정) 행번호 열번호 바뀔 것임 수정 필요
                    cal_row = int(data) 
                else:
                    col = rc_num
                    cal_col = int(data)

                if pair_check.count(pair_cal) == 2: # 가로 세로 행이 2개 다 들어왔으면
                    result = sum(x * y for x, y in zip(cal_row, cal_col))
                    msg = "cal_result" + str(result) + str(5) + str(row) + str(col)
                    pair_check = [x for x in pair_check if x != pair_cal]
                    client_sock.send(bytes(msg.encode()))
        except:
            pass


#클라이언트가 받는 경우
#- 처음 서버한테 자기가 행렬(가로, 세로)를 주는 아인지 받는 아인지 확인
#- 행렬을 받음

def Recv(client_sock, send_queue):
    while True:
        recv_data = client_sock.recv(1024).decode()  # Server -> Client 데이터 수신
        print(recv_data)
        
        if recv_data.split()[1] == 'Client_all_connected':
            msg = 'Start 0 0 0 0'
            client_sock.send(bytes(msg.encode()))

        else:
            send_queue.put([recv_data])

#TCP Client
if __name__ == '__main__':
    send_queue = Queue()
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #TCP Socket
    Host = 'localhost' #통신할 대상의 IP 주소
    Port = 9000  #통신할 대상의 Port 주소
    client_sock.connect((Host, Port)) #서버로 연결시도
    print('Connecting to ', Host, Port)

    matrix = np.random.randint(0, 101, (10, 10)) # 10X10 행렬 만들기 


    #Client의 메시지를 보낼 쓰레드
    thread1 = threading.Thread(target=Send, args=(client_sock, send_queue))
    thread1.start()

    #Server로 부터 다른 클라이언트의 메시지를 받을 쓰레드
    thread2 = threading.Thread(target=Recv, args=(client_sock, send_queue))
    thread2.start()