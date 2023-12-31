import socket
import threading
from queue import Queue
import numpy as np
import random
import time


# 시간을 출력 형식에 맞게 변환
def real_time(time):
    m = time // 60
    h = m // 60
    m = m % 60
    s = time % 60

    second = "{}".format(s)
    minute = "{}".format(m)
    hour = "{}".format(h)
    result = "{}:{}:{}".format(hour.zfill(2), minute.zfill(2), second.zfill(2))
    # 예) 3초 => 00:03 / 100초 => 01:40
    return result


def recv_client_choice_lottery(ticket_list1, client_num1, ticket_list2, client_num2):

    if len(ticket_list1) == 0 and len(ticket_list2) == 0:
        return (-1, -1, -1, -1)

    choice_ticket = random.choice(ticket_list1 + ticket_list2) # client1이 가지고있는 티켓 [1, 2, 3, 4]와 client2가 가지고있는 티켓 [5, 6, 7, 8]중에 하나 선택
    
    if choice_ticket in ticket_list1: # 선택한 티켓이 누가 가진 티켓인지 검사
        ticket_list1.remove(choice_ticket) # 뽑혔던 티켓 없애기
        return (client_num1, ticket_list1, client_num2, ticket_list2) 
    else:
        ticket_list2.remove(choice_ticket) # 두 번째로 선택된 클라이언트에 대하여 위와 똑같이 실행
        return (client_num2, ticket_list2, client_num1, ticket_list1)

def empty_check(idx, matrix):
    empty_space = [] 
    for m in range(0, 10):
        for n in range(0, 10):
            if matrix[idx][m][n] == -1:
                empty_space.append([m, n])
    
    random_mat = random.choice(empty_space)

    return random_mat

def Send(group, send_queue):
    global result_matrix_count, result_matrix, matrix, case, dic, c_list, system_clock_formating, system_clock
    msg = "first_connected " + str(len(group)) + " " + str(result_matrix_count) + " " + str(system_clock)
    group[-1].send(bytes(msg.encode()))

    matrix_counting = 0
    while True:
        try:
            recv = send_queue.get()
            #새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감
            if recv == 'Group Changed':
                break

            type_name, pair_mul, data, recv_client_num, rc, rc_num, etc = recv[0].split()
            
            system_clock = int(system_clock)

            system_clock += 1

            if type_name == "matrix": # 클라이언트에게 행렬을 받아왔다면
                time.sleep(0.03)
                system_clock_formating = real_time(system_clock)
                if rc == "row":
                    server_file.write("{} [server] 클라이언트 {}에게 '행'의 정보를 전달합니다.\n".format(system_clock_formating, recv_client_num))
                elif rc == "col":
                    server_file.write("{} [server] 클라이언트 {}에게 '열'의 정보를 전달합니다.\n".format(system_clock_formating, recv_client_num))                    
                recv_client = group[int(recv_client_num)-1] # 연산을 해야하는 클라이언트에게 메시지 전송
                msg = recv_client_num + " calculating " + pair_mul + " " + data + "|" + rc + "|" + rc_num + "|" + etc + " " + str(system_clock)
                recv_client.send(bytes(msg.encode())) #메시지 전송
                system_clock += 1

            elif type_name == "cal_result":
                time.sleep(0.02)

                #다시 행렬을 받을 (연산역할) 클라이언트를 랜덤으로 선정
                recv_client_t = recv_client_num
                
                recv_client_ticket, not_recv_client, not_recv_client_ticket = etc.split("|")

                if recv_client_ticket == "[]" and not_recv_client_ticket == "[]":
                    recv_client_ticket = []
                    not_recv_client_ticket = []
                
                elif recv_client_ticket == "[]" or not_recv_client_ticket == "[]":
                    if recv_client_ticket == "[]":
                        recv_client_ticket = []
                        not_recv_client_ticket = list(map(int, not_recv_client_ticket.split(",")))
                    if not_recv_client_ticket == "[]":
                        not_recv_client_ticket = []
                        recv_client_ticket = list(map(int, recv_client_ticket.split(",")))
                
                else:
                    # 연산할 클라이언트 2명이 가지고 있는 티켓 리스트로
                    recv_client_ticket = list(map(int, recv_client_ticket.split(",")))
                    not_recv_client_ticket = list(map(int, not_recv_client_ticket.split(",")))
                

                # 클라이언트 2명 중 한명 선택
                recv_client_t, recv_client_ticket, not_recv_client, not_recv_client_ticket = recv_client_choice_lottery(recv_client_ticket, int(recv_client_t), not_recv_client_ticket, int(not_recv_client))

                idx = dic[pair_mul]
                matrix[idx][int(rc)][int(rc_num)] = int(data) # idx: case 인덱스, rc: 행, rc_num:열
                system_clock += 1
                system_clock_formating = real_time(system_clock)
                server_file.write("{} [server] 연산 결과를 해당 행렬의 [{},{}] 에 저장합니다.\n".format(system_clock_formating, rc, rc_num ))
                # 실행시켜보면 티켓의 수가 둘다 0이 되면 끝남. 즉 100번 실행하면 끝난다는 소리
                
                complete = 1

                for m_row in matrix[idx]:
                    if -1 in m_row:
                        complete = 0
                        break
                
                if complete == 0:
                    #Recv에 있던거랑 똑같음
                    if len(recv_client_ticket) == 0:
                        str_recv_client_ticket = "[]"
                    else:
                        str_recv_client_ticket = ','.join(map(str, recv_client_ticket))

                    if len(not_recv_client_ticket) == 0:
                        str_not_recv_client_ticket = "[]"
                    else:
                        str_not_recv_client_ticket = ','.join(map(str, not_recv_client_ticket))

                    
                    random_mat = empty_check(idx, matrix) # 랜덤 빈 좌표
                    add_msg = ' matrix ' + ','.join(map(str, case[idx])) + " " + str(recv_client_t) + "|" + str_recv_client_ticket + "|" + str(not_recv_client) + "|" + str_not_recv_client_ticket
                    for j, m in zip(case[idx], random_mat): # 메시지 전송
                        msg = str(j) + "=" + str(m) + " " + add_msg + " " + str(system_clock)
                        group[j-1].send(bytes(msg.encode())) #group에는 들어온 클라이언트가 하나씩 순서대로 쌓여있기때문에 인덱스로 골라서 send
                        msg = add_msg
                
                else:
                    matrix_counting += 1

                    if matrix_counting == 6:
                        server_file.write("{} [server] '라운드 {}' 완료\n".format(system_clock_formating, result_matrix_count))

                        for k, con in enumerate(group):
                            msg = "round_pass " + str(k+1) + " " + str(result_matrix_count) + " " + str(system_clock)
                            con.send(bytes(msg.encode()))

                        result_matrix_count += 1
                        result_matrix.append(matrix)
                        result_time.append(system_clock-result_time[-1])

                        if result_matrix_count == 3:
                            for k, con in enumerate(group):
                                msg = "round_over " + str(k+1) + " " + str(result_matrix_count) + " " + str(system_clock)
                                con.send(bytes(msg.encode()))
                            print("접속 종료")
                            server_file.write("{} [server] 모든 라운드를 실행하였습니다.\n".format(system_clock_formating))
                            for i,mtx,t in zip(range(1,3),result_matrix, result_time[1:]):
                                for j, m in zip(range(1,7),mtx):
                                    print("Round {} matrix {}\n {}\n".format(i, j, m))
                                    server_file.write("Round {} matrix {}\n {}\n".format(i, j, m))
                                print("소요시간 : {} sec\n\n".format(t))
                                server_file.write("소요시간 : {} sec\n\n".format(t))
                            break

                        server_file.write("{} [server] '라운드 {}' 시작\n".format(system_clock_formating, result_matrix_count))
                        for k, con in enumerate(group):
                            msg = "make_new_matrix " + str(k+1) + " " + str(result_matrix_count) + " " + str(system_clock)
                            con.send(bytes(msg.encode()))


                        matrix = np.full((6, 10, 10), -1)
                        matrix_counting = 0
                        for i in case: # 클라이언트에게 행렬을 달라고 알리는 메시지 전송
                            ticket_list1 = [ i for i in range(50)] #각 경우의 수 마다 연산할 클라이언트에게 티켓 주기
                            ticket_list2 = [ i for i in range(50, 100)]
                            complement = list(set(c_list) - set(i)) #행렬을 받을 클라이언트 둘
                            pair_mul = i[0] * i[1] # 결과 행렬 구분할 변수
                            idx = dic[str(pair_mul)]
                            #행렬을 받을 클라이언트 랜덤으로 선택 ( 선택된 클라이언트 번호, 선택된 클라이언트가 가진 티켓, 선택되지않은 클라이언트 번호, 선택되지않은 클라이언트가 가진 티켓 )
                            recv_client, recv_client_ticket, not_recv_client, not_recv_client_ticket = recv_client_choice_lottery(ticket_list1, complement[0], ticket_list2, complement[1])
                            
                            random_mat = empty_check(idx, matrix) # 랜덤 빈 좌표
                            
                            #나중에 티켓정보가 필요하기 때문에 메시지 주고받을때 계속해서 붙여줌
                            add_msg = ' matrix ' + ','.join(map(str, i)) + " " + str(recv_client) + "|" + ','.join(map(str, recv_client_ticket)) + "|" + str(not_recv_client) + "|" + ','.join(map(str, not_recv_client_ticket)) + " " + str(system_clock)
                            for j, m in zip(i, random_mat): # 메시지 전송 (클라이언트 번호, 좌표)
                                time.sleep(0.01)
                                # 여기서 빈 공간(-1)을 좌표로 모아서 해당 클라이언트에게 보냄
                                #print("클라이언트" + str(j) + "에게 행렬을 보내달라 말함")
                                msg = str(j) + "=" + str(m) + " " + add_msg # 클라이언트 번호, 좌표 (차례대로 행, 열 보내짐) + 위에 만든 메시지
                                group[j-1].send(bytes(msg.encode()))
                                msg = add_msg
                        
        except:
            pass

    if result_matrix_count == 3:
        server_sock.close()
        

    
# 서버가 받는 경우
#- 행렬 받기
#- 연산결과 받기

def Recv(conn, count, send_queue, group):
    global case, dic, c_list, result_matrix_count, system_clock_formating, system_clock

    matrix = np.full((6, 10, 10), -1)
    
    if count == 4: #처음 클라이언트 4명이 다 들어오면 실행        print(5)
        server_file.write("{} [server] '라운드 {}' 시작\n".format(system_clock_formating, result_matrix_count))
        for i in case: # 클라이언트에게 행렬을 달라고 알리는 메시지 전송
            ticket_list1 = [ i for i in range(50)] #각 경우의 수 마다 연산할 클라이언트에게 티켓 주기
            ticket_list2 = [ i for i in range(50, 100)]
            complement = list(set(c_list) - set(i)) #행렬을 받을 클라이언트 둘
            pair_mul = i[0] * i[1] # 결과 행렬 구분할 변수
            idx = dic[str(pair_mul)]
            #행렬을 받을 클라이언트 랜덤으로 선택 ( 선택된 클라이언트 번호, 선택된 클라이언트가 가진 티켓, 선택되지않은 클라이언트 번호, 선택되지않은 클라이언트가 가진 티켓 )
            recv_client, recv_client_ticket, not_recv_client, not_recv_client_ticket = recv_client_choice_lottery(ticket_list1, complement[0], ticket_list2, complement[1])
            
            random_mat = empty_check(idx, matrix) # 랜덤 빈 좌표
            
            #나중에 티켓정보가 필요하기 때문에 메시지 주고받을때 계속해서 붙여줌
            add_msg = ' matrix ' + ','.join(map(str, i)) + " " + str(recv_client) + "|" + ','.join(map(str, recv_client_ticket)) + "|" + str(not_recv_client) + "|" + ','.join(map(str, not_recv_client_ticket)) 
            for j, m in zip(i, random_mat): # 메시지 전송 (클라이언트 번호, 좌표)
                time.sleep(0.01)
                msg = str(j) + "=" + str(m) + add_msg + " " + str(system_clock) # 클라이언트 번호, 좌표 (차례대로 행, 열 보내짐) + 위에 만든 메시지
                group[j-1].send(bytes(msg.encode())) #클라이언트에게 행/열 전송 요청
                msg = add_msg


    while True:
        
        if result_matrix_count == 3: 
            break

        data = conn.recv(1024).decode()
        send_queue.put([data, conn, count]) #각각의 클라이언트의 메시지, 소켓정보, 쓰레드 번호를 send로 보냄
    
    server_sock.close()

# TCP Echo Server
if __name__ == '__main__':
    
    send_queue = Queue()
    HOST = ''  # 수신 받을 모든 IP를 의미
    PORT = 9000  # 수신받을 Port
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP Socket
    server_sock.bind((HOST, PORT))  # 소켓에 수신받을 IP주소와 PORT를 설정
    server_sock.listen(5)  # 소켓 연결, 여기서 파라미터는 접속수를 의미
    count, result_matrix_count = 0, 1
    group, result_matrix, result_time = [], [], [0] #연결된 클라이언트의 소켓정보를 리스트로 묶기 위함
    case = [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]
    c_list = [1, 2, 3, 4]
    dic = {'2': 0, '3': 1, '4': 2, '6': 3, '8': 4, '12': 5}
    matrix = np.full((6, 10, 10), -1)

    system_clock = 0
    system_clock_formating = real_time(system_clock)

    server_file = open("server_log.txt", "w", encoding="UTF-8")

    server_file.write("{} [server] 10x10 행렬을 6개 생성합니다.\n".format(system_clock_formating))
    
    for i, m in zip(range(1,7),matrix):
        server_file.write("matrix {}\n {}\n".format(i, m))
    server_file.write("\n")

    while True:
        try:
            count = count + 1
            conn, addr = server_sock.accept()  # 해당 소켓을 열고 대기
            group.append(conn) #연결된 클라이언트의 소켓정보
            print('Connected ' + str(addr))

            server_file.write("{} [server] '클라이언트 {}' (이)가 접속하였습니다.\n".format(system_clock_formating, len(group)))

            #소켓에 연결된 모든 클라이언트에게 동일한 메시지를 보내기 위한 쓰레드(브로드캐스트)
            #연결된 클라이언트가 1명 이상일 경우 변경된 group 리스트로 반영

            if count > 1:
                send_queue.put('Group Changed')
                thread1 = threading.Thread(target=Send, args=(group, send_queue,))
                thread1.start()
                pass
            else:
                thread1 = threading.Thread(target=Send, args=(group, send_queue,))
                thread1.start()

            #소켓에 연결된 각각의 클라이언트의 메시지를 받을 쓰레드
            thread2 = threading.Thread(target=Recv, args=(conn, count, send_queue, group))
            thread2.start()

            
        except:
            exit(0)