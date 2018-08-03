/*
 * pi_imu_interface.cpp
 *
 *  Created on: Aug 1, 2018
 *      Author: Marcelo
 */
#include <carmen/carmen.h>
#include <carmen/xsens_messages.h>
#include <carmen/xsenscore.h>
#include <GL/glut.h>
#include <math.h>

#define RAD_TO_DEG 57.29578
#define M_PI 3.14159265358979323846
#define AA 0.97 // complementary filter constant

carmen_xsens_global_quat_message *xsens_quat_message;
xsens_global data;
GLfloat angle, fAspect;

void
shutdown_module(int signo)
{
    if (signo == SIGINT)
    {
        carmen_ipc_disconnect();

        printf("Imu Interface: disconnected.\n");
        exit(0);
    }
}


void
xsens_message_handler(carmen_xsens_global_quat_message *xsens_quat_message)
{
	data.acc.x = xsens_quat_message->m_acc.x;
	data.acc.y = xsens_quat_message->m_acc.y;
	data.acc.z = xsens_quat_message->m_acc.z;

	data.gyr.x = xsens_quat_message->m_gyr.x;
	data.gyr.y = xsens_quat_message->m_gyr.y;
	data.gyr.z = xsens_quat_message->m_gyr.z;

	data.mag.x = xsens_quat_message->m_mag.x;
	data.mag.y = xsens_quat_message->m_mag.y;
	data.mag.z = xsens_quat_message->m_mag.z;
/*
	printf("ACELEROMETRO = X:%f m/s^2 Y:%f m/s^2 Z:%f m/s^2\n", data.acc.x, data.acc.y, data.acc.z);
	printf("GIROSCÓPIO = X:%f radps Y:%f radps Z:%f radps\n", data.gyr.x, data.gyr.y, data.gyr.z);
	printf("MAGNETOMETRO = X:%f mgauss Y:%f mgauss Z:%f mgauss\n", data.mag.x, data.mag.y, data.mag.z);*/
}


void
carmen_xsens_subscribe_xsens_global_quat_message(carmen_xsens_global_quat_message
					    *xsens_global,
					    carmen_handler_t handler,
					    carmen_subscribe_t subscribe_how)
{
    carmen_subscribe_message((char *) CARMEN_XSENS_GLOBAL_QUAT_NAME,
    						 (char *) CARMEN_XSENS_GLOBAL_QUAT_FMT,
                             xsens_global, sizeof(carmen_xsens_global_quat_message),
            			     handler, subscribe_how);
}


void
carmen_xsens_unsubscribe_xsens_global_quat_message(carmen_handler_t handler)
{
  carmen_unsubscribe_message((char *) CARMEN_XSENS_GLOBAL_QUAT_NAME, handler);
}


void
display (void)
{
	float AccYangle = 0.0;
	float AccXangle = 0.0;
	float AccZangle = 0.0;

	float CFangleX = 0.0;
	float CFangleY = 0.0;
	float CFangleZ = 0.0;
	//Convert Accelerometer values to degrees
	AccXangle = (float) (atan2(data.acc.y, data.acc.z)) * RAD_TO_DEG;
	AccYangle = (float) (atan2(data.acc.z, data.acc.x)) * RAD_TO_DEG;
	AccZangle = (float) (atan2(data.acc.x, data.acc.y)) * RAD_TO_DEG;

	printf ("X : %f\n", AccXangle);
	printf ("Y : %f\n", AccYangle);
	printf ("Z: %f\n", AccZangle);
	/*
	AccXangle -= (float)180.0;
	if (AccYangle > 90)
		AccYangle -= (float)270;
	else
		AccYangle += (float)90;

*/

	//Complementary filter used to combine the accelerometer and gyro values.
	CFangleX=AA*(CFangleX + data.gyr.x) + (1 - AA) * AccXangle;
	CFangleY=AA*(CFangleY + data.gyr.y) + (1 - AA) * AccYangle;
	CFangleZ=AA*(CFangleZ + data.gyr.z) + (1 - AA) * AccZangle;

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	glColor3f(0.0f, 0.0f, 1.0f);
	glPushMatrix();
		glRotatef(AccXangle, 1.0, 0.0, 0.0);
		glRotatef(AccYangle, 0.0, 1.0, 0.0);
		glRotatef(AccZangle, 0.0, 0.0, 1.0);
		// Desenha o teapot com a cor corrente (wire-frame)
		glutSolidCube(50.0f);
	glPopMatrix();
	// Executa os comandos OpenGL
	glutSwapBuffers();
}


void
sleep_ipc()
{
	carmen_ipc_sleep(0.033333333);
	glutPostRedisplay();
}


// Inicializa parâmetros de rendering
void Inicializa (void)
{
	GLfloat luzAmbiente[4]={0.2,0.2,0.2,1.0};
	GLfloat luzDifusa[4]={0.7,0.7,0.7,1.0};	   // "cor"
	GLfloat luzEspecular[4]={1.0, 1.0, 1.0, 1.0};// "brilho"
	GLfloat posicaoLuz[4]={0.0, 50.0, 50.0, 1.0};

	// Capacidade de brilho do material
	GLfloat especularidade[4]={1.0,1.0,1.0,1.0};
	GLint especMaterial = 80;

	// Especifica que a cor de fundo da janela será preta
	glClearColor(0.0f, 0.0f, 0.0f, 1.0f);

	// Habilita o modelo de colorização de Gouraud
	glShadeModel(GL_SMOOTH);

	// Define a refletância do material
	glMaterialfv(GL_FRONT,GL_SPECULAR, especularidade);
	// Define a concentração do brilho
	glMateriali(GL_FRONT,GL_SHININESS,especMaterial);

	// Ativa o uso da luz ambiente
	glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luzAmbiente);

	// Define os parâmetros da luz de número 0
	glLightfv(GL_LIGHT0, GL_AMBIENT, luzAmbiente);
	glLightfv(GL_LIGHT0, GL_DIFFUSE, luzDifusa );
	glLightfv(GL_LIGHT0, GL_SPECULAR, luzEspecular );
	glLightfv(GL_LIGHT0, GL_POSITION, posicaoLuz );

	// Habilita a definição da cor do material a partir da cor corrente
	glEnable(GL_COLOR_MATERIAL);
	//Habilita o uso de iluminação
	glEnable(GL_LIGHTING);
	// Habilita a luz de número 0
	glEnable(GL_LIGHT0);
	// Habilita o depth-bufferingt
	glEnable(GL_DEPTH_TEST);

	angle=45;
}

// Função usada para especificar o volume de visualização
void EspecificaParametrosVisualizacao(void)
{
	// Especifica sistema de coordenadas de projeção
	glMatrixMode(GL_PROJECTION);
	// Inicializa sistema de coordenadas de projeção
	glLoadIdentity();
	// Especifica a projeção perspectiva
	gluPerspective(angle,fAspect,0.1,500);
	// Especifica sistema de coordenadas do modelo
	glMatrixMode(GL_MODELVIEW);
	// Inicializa sistema de coordenadas do modelo
	glLoadIdentity();
	// Especifica posição do observador e do alvo
	gluLookAt(0,80,200, 0,0,0, 0,1,0);
}


// Função callback chamada quando o tamanho da janela é alterado
void
AlteraTamanhoJanela(GLsizei w, GLsizei h)
{
	// Para previnir uy = 0;ma divisão por zero
	if ( h == 0 ) h = 1;
	// Especifica o tamanho da viewport
	glViewport(0, 0, w, h);
	// Calcula a correção de aspecto
	fAspect = (GLfloat)w / (GLfloat)h;
	EspecificaParametrosVisualizacao();
}


// Função callback chamada para gerenciar eventos do mouse
void
GerenciaMouse(int button, int state, int x, int y)
{
	x += 0;
	y += 0;
	if (button == GLUT_LEFT_BUTTON)
		if (state == GLUT_DOWN)
		{  // Zoom-in
			if (angle >= 10) angle -= 5;
		}
	if (button == GLUT_RIGHT_BUTTON)
		if (state == GLUT_DOWN)
		{  // Zoom-out
			if (angle <= 130) angle += 5;
		}
	EspecificaParametrosVisualizacao();
	glutPostRedisplay();
}

int
main(int argc, char *argv[])
{
	carmen_ipc_initialize(argc, argv);

	carmen_param_check_version(argv[0]);

	signal(SIGINT, shutdown_module);

	carmen_xsens_subscribe_xsens_global_quat_message(xsens_quat_message, (carmen_handler_t) xsens_message_handler, CARMEN_SUBSCRIBE_LATEST);

	glutInit(&argc, argv); // Initialize GLUT
	glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB);
	glutInitWindowSize(800, 800);
	glutCreateWindow("Visualizacao 3D");
	glutDisplayFunc(display);
	glutReshapeFunc(AlteraTamanhoJanela);
	glutMouseFunc(GerenciaMouse);
	Inicializa();
	glutIdleFunc(sleep_ipc);
	glutMainLoop();

	return (0);
}
