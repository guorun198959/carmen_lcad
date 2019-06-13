#include <carmen/carmen.h>
#include <control.h>
#include <sys/socket.h>
#include <netdb.h>

#define PORT 3458

int server_fd;


int
connect_with_client()
{
    int new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);

    // Creating socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0)
    {
        perror("--- Socket Failed ---\n");
        return (-1);
    }
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt)))
    {
        perror("--- Setsockopt Failed ---\n");
        return (-1);
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons( PORT );
    
    // Forcefully attaching socket to the port defined
    if (bind(server_fd, (struct sockaddr*) &address, sizeof(address)) < 0)
    {
        perror("--- Bind Failed ---\n");
        return (-1);
    }
    if (listen(server_fd, 3) < 0)
    {
        perror("-- Listen Failed ---\n");
        return (-1);
    }
    
    printf("--- Waiting for connection! --\n");
    if ((new_socket = accept(server_fd, (struct sockaddr*) &address, (socklen_t*) &addrlen)) < 0)
    {
        perror("--- Accept Failed ---\n");
        return (-1);
    }
    printf("--- Connection established successfully! ---\n");

	return (new_socket);
}


void
build_odometry_socket_msg(carmen_base_ackerman_odometry_message *msg, double *array)
{
	array[0] = msg->x;
	array[1] = msg->y;
	array[2] = msg->theta;
	array[3] = msg->v;
	array[4] = msg->phi;
}


///////////////////////////////////////////////////////////////////////////////////////////////


//////////////////////////////////////////////////////////////////////////////////////////////////
//                                                                                              //
// Handlers                                                                                     //
//                                                                                              //
//////////////////////////////////////////////////////////////////////////////////////////////////


void
base_ackerman_odometry_handler(carmen_base_ackerman_odometry_message *msg)
{
	double array[5];

	build_odometry_socket_msg(msg, array);

	static int pi_socket = 0;
	int result = 0;

	if (pi_socket == 0)
		pi_socket = connect_with_client();

	//printf ("%lf %lf %lf %lf %lf\n", array[0], array[1], array[2], array[3], array[4]);

	result = send(pi_socket, array, 40, MSG_NOSIGNAL);					// The socket returns the number of bytes read, 0 in case of connection lost, -1 in case of error

	if (result == 0 || result == -1)									// 0 Connection lost due to server shutdown -1 Could not connect
	{
		close(pi_socket);
		pi_socket = connect_with_client();
		return;
	}
}


void
robot_ackerman_velocity_handler(carmen_robot_ackerman_velocity_message *msg)
{
	double array[5];
	static int pi_socket = 0;
	int result = 0;

	if (pi_socket == 0)
		pi_socket = connect_with_client();

	array[0] = msg->v;
	array[1] = msg->phi;

	//printf ("v: %lf phi: %lf\n", array[0], array[1]);

	result = send(pi_socket, array, 40, MSG_NOSIGNAL);					// The socket returns the number of bytes read, 0 in case of connection lost, -1 in case of error

	if (result == 0 || result == -1)									// 0 Connection lost due to server shutdown -1 Could not connect
	{
		close(pi_socket);
		pi_socket = connect_with_client();
		return;
	}
}


static void
shutdown_module(int x)            // Handles ctrl+c
{
	if (x == SIGINT)
	{
		carmen_ipc_disconnect();
		carmen_warn("\nDisconnected.\n");
		exit(0);
	}
}
//////////////////////////////////////////////////////////////////////////////////////////////////


int
subscribe_to_relevant_messages()
{
	carmen_base_ackerman_subscribe_odometry_message_2(NULL, (carmen_handler_t) base_ackerman_odometry_handler, CARMEN_SUBSCRIBE_LATEST);

	return (0);
}


//int
//initialize_ipc(void)
//{
//	IPC_RETURN_TYPE err;
//
//	err = IPC_defineMsg(CARMEN_BASE_ACKERMAN_ODOMETRY_2_NAME, IPC_VARIABLE_LENGTH, CARMEN_BASE_ACKERMAN_ODOMETRY_2_NAME);
//
//	if (err != IPC_OK)
//		return -1;
//
//	return 0;
//}


int
main(int argc, char **argv)
{
	carmen_ipc_initialize(argc, argv);

	carmen_param_check_version(argv[0]);

	signal(SIGINT, shutdown_module);

//	if (initialize_ipc() < 0)
//		carmen_die("Error in initializing ipc...\n");

	if (subscribe_to_relevant_messages() < 0)
		carmen_die("Error subscribing to messages...\n");

	carmen_ipc_dispatch();

	return (0);
}
