#include <SoftwareSerial.h>

SoftwareSerial bluetoothSerial(7,8); // RX, TX pins on Teensy

#include <SD.h>

#include <iostream>

File dataFile; // Variable para archivos csv
int contadorCal; // Variable para calibración
char receivedDataCal[6]; // Array para guardar los datos recibidos de calibración
int habilitadorCal = 0;
String ang_formula;
String v_formula;
int dataIndexCal =0; 
int tipo_ej = 0; // 0 es para flexion

float pendiente_formula = 0.2469;
float v_punto_formula = 0;
float ang_punto_formula = -149.08;



int LDR = A6; // Pin para medir pot (14)
float k_resorte =1; // Número de resorte a utilizar
char receivedDataResorte[1];
int dataIndexResorte = 0;
int habilitadorResorte = 0;
String Resorte;
int identificador_brazo =0;
char letra ='F';



// Variables de flexión:
int numExtFlex[12000]; // Array para guardar los datos de angulo de extensión y flexión
float fuerzaExtFlex[10000]; // Array para guardar los datos de fuerza asociada a la extensión y flexión
int contadorFlex = 0; // Contador para saber "cuando" enviar los datos para la actualización del carro en el juego
int anguloFlexMayor = 0; // Ángulo de flexion máximo alcanzado
float fuerzaFlexMayor = 0; // Fuerza flexión máxima alcanzada
char receivedDataIDFlex[18]; // Datos recibidos de la ID de la persona para flexion
char receivedDataNombreFlex[255]; // datos recibidos del nombre de la persona 
int dataIndexIDFlex = 0; // Iterador para guardar los datos del ID en el array correspondiente
int dataIndexNombreFlex = 0; // Iterador guardar los datos del nombre en el array correspondiente
int habilitadorCedulaFlex = 0; //  Habilitador para saber cuando empezar a guardar los datos del ID y cuando terminar
int habilitadorNombreFlex = 0; //  Habilitador para saber cuando empezar a guardar los datos del nombre y cuando terminar
String nombreFlex; // Aquí se almacenan los caracteres del array de nombre concatenados en una sola variable
String IDFlex; // Aquí se almacena el ID concatenado con el que se guardará el documento csv
String IDFlexDoc; // Codigo del ejercicio que irá en el documento (0 para flexion)
int tamanoFlex = 0; // Iterador para guardar los datos de angulo de flexion en el array. También se utiliza como iterador para el array de fuerza
int Angulo_MayorFlex = 0; // Variable para saber si en cada ciclo de ejercicio se alcanzó el ángulo meta
int Rep_ExitosasFlex = 0; // Para contar las repeticiones exitosas de flexion
int Rep_IncompletasFlex = 0; // Para contar las repeticiones incompletas de flexion
int habilitadorFlex = 0; // Indica cuando comienza una nueva repetición de flexion
char receivedDataAnguloFlex[2]; // Para almacenar el ángulo meta
int dataIndexAnguloFlex = 0; // Iterador para guardar los datos de angulo meta en el array
int habilitadorAnguloFlex = 0; // Habilitador para saber cuando empezar a guardar los datos angulo meta y cuando terminar
String AnguloFlex; // Almacena los valores concatenados del angulo meta guardado en el array
int anguloScreenFlex;


void setup() {
  //Serial.begin(38400); // Inicializar el puerto serial para la comunicación con la computadora
  bluetoothSerial.begin(9600); // Inicializar el puerto serial para el módulo Bluetooth HC-05
  pinMode(LDR, INPUT); // Pin 14 como entrada


  // Inicializar la tarjeta SD
  if (!SD.begin(BUILTIN_SDCARD)) {
    //Serial.println("Error al iniciar la tarjeta SD");
   
  }
}

void loop() {
  if (bluetoothSerial.available()) {
    char recibido = bluetoothSerial.read(); // Leer el primer carácter recibido

// PARA FLEXION:

    // Si se recibe un 'a', indica que los siguientes caracteres que vienen son el ID (flex) 
    // Se activa el habilitador

    if (recibido == 'a') {
      habilitadorCedulaFlex = 1;
      dataIndexIDFlex = 0;
      IDFlex = "";
      memset(receivedDataIDFlex,' ',18);
    }

    // Si se recibe un 'b', indica que ya llegaron todos los caracteres del ID (Flex)
    // Se guardan todos los datos del array en una sola variable
    // Se desactiva el habilitador

    if (recibido == 'b'){
      char brazo = 'D';
      if (tipo_ej == 0){
      IDFlexDoc = "0"; // 0 para flexion
      letra = 'F';
      }
      else{
        IDFlexDoc = "1";
        letra = 'E';
      }

      if (identificador_brazo == 0){
      brazo = 'D'; // 0 para derecho
      }
      else{
        brazo = 'I';
      }
      habilitadorCedulaFlex = 0;
      //Serial.println("ID:");
      receivedDataIDFlex[12] = brazo;
      receivedDataIDFlex[13] = letra; // Se agrega una como distintivo de flexion
      receivedDataIDFlex[14] = '.';
      receivedDataIDFlex[15] = 'c';
      receivedDataIDFlex[16] = 's';
      receivedDataIDFlex[17] = 'v';

      for (int i = 0; i <18; i++){
        IDFlex = IDFlex +receivedDataIDFlex[i];
      }
      
      //Serial.println(IDFlex);
      //Serial.println(IDFlexDoc);

    }

    // Si el habilitador está activo, entonces se guardan todos los datos recibidos en el array de ID (Flex)

    if ((habilitadorCedulaFlex ==1) & (recibido != 'a')){
      receivedDataIDFlex[dataIndexIDFlex] = recibido;
      dataIndexIDFlex++;
      //delay(100);
    }

    // Si se recibe un 'e', indica que los siguientes caracteres que vienen son el ángulo meta (Flex) 
    // Se activa el habilitador

    if (recibido == 'e') {
      habilitadorAnguloFlex = 1;
      dataIndexAnguloFlex = 0;
      AnguloFlex = ""; 
      memset(receivedDataAnguloFlex,' ',2);
    }

    // Si se recibe un 'f', indica que ya llegaron todos los caracteres del ángulo meta (Flex)
    // Se guardan todos los datos del array en una sola variable
    // Se desactiva el habilitador

    if (recibido == 'f'){
      habilitadorAnguloFlex = 0;
      
      for (int i = 0; i <2; i++){
        AnguloFlex = AnguloFlex +receivedDataAnguloFlex[i];
      }
      //Serial.println("ANGULO:");
      //Serial.println(AnguloFlex);
    }

    // Si el habilitador está activo, entonces se guardan todos los datos recibidos en el array de angulo meta (Flex)

    if ((habilitadorAnguloFlex ==1) & (recibido != 'e')){
      receivedDataAnguloFlex[dataIndexAnguloFlex] = recibido;
      dataIndexAnguloFlex++;
      //delay(100);
    }

    // Si se recibe un '*', indica que los siguientes caracteres que vienen son el nombre (Flex) 
    // Se activa el habilitador

    if (recibido == '*') {
      //Serial.println("NOMBRE:");
      habilitadorNombreFlex = 1;
      habilitadorCedulaFlex = 0;
      dataIndexNombreFlex = 0;
      nombreFlex = "";
    }

    // Si se recibe un '+', indica que ya llegaron todos los caracteres del nombre (Flex)
    // Se guardan todos los datos del array en una sola variable
    // Se desactiva el habilitador

    if (recibido == '+'){
      habilitadorNombreFlex = 0;
      //Serial.println("AHORA NOMBRE:");
      for (int i = 0; i<dataIndexNombreFlex; i++){
        nombreFlex = nombreFlex+receivedDataNombreFlex[i];
      }
      //Serial.println(nombreFlex);
    }
    
    // Si el habilitador está activo, entonces se guardan todos los datos recibidos en el array de nombre (Flex)

    if ((habilitadorNombreFlex ==1) & (recibido != '*')){
      //Serial.println(dataIndexNombreFlex);
      receivedDataNombreFlex[dataIndexNombreFlex] = recibido;
      dataIndexNombreFlex++;
      
    }

    // Si se recibe un 'c', indica que se está en el juego de flexión
    // Se ponen todos los iteradores en 0 

    if (recibido == 'c'){
      memset(numExtFlex,0,tamanoFlex);
      memset(fuerzaExtFlex,0,tamanoFlex);
      contadorFlex = 0;
      tamanoFlex =0;
     // Serial.println("OPCIONES:");
     // Serial.println(identificador_brazo);
     // Serial.println(tipo_ej);
      
   
    }

    // Mientras el último recibido sea 'c', se envían los datos a la app y se almacenan en un array
    // Se calcula el valor de fuerza
    // Se cuentan cuantas repeticiones fueron correctas e incorrectas

    while (recibido == 'c'){
      int data = analogRead(LDR);
      int anguloFLEX;
      //Serial.println("OPCIONES:");
      //Serial.println(identificador_brazo);
      //Serial.println(tipo_ej);
      
      //delay(2000);
      if (identificador_brazo == 0 && tipo_ej == 0){
        anguloFLEX = pendiente_formula*(data-v_punto_formula)+ang_punto_formula; // CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
      }
      else if (identificador_brazo == 1 && tipo_ej == 0){
        anguloFLEX = -(pendiente_formula*(data-v_punto_formula)+ang_punto_formula); // CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
      }
      else if (identificador_brazo == 0 && tipo_ej == 1){
        anguloFLEX = -(pendiente_formula*(data-v_punto_formula)+ang_punto_formula); // CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
      }
      else if (identificador_brazo == 1 && tipo_ej == 1){
        anguloFLEX = (pendiente_formula*(data-v_punto_formula)+ang_punto_formula); // CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
      }
      //Serial.println(anguloFLEX);
     
      float fuerzaF = k_resorte*37.3823e-6*anguloFLEX;
      numExtFlex[tamanoFlex] = anguloFLEX;
      fuerzaExtFlex[tamanoFlex] = fuerzaF;

      if (anguloFLEX >= anguloFlexMayor){
        anguloFlexMayor = anguloFLEX; 
      }

      if (fuerzaF >= fuerzaFlexMayor){
        fuerzaFlexMayor = fuerzaF;
      }

      // Si el angulo es mayor a 3 y el habilitador es 0, se comienza un nuevo ciclo de ejercicio

      if ((anguloFLEX >3)&&(habilitadorFlex == 0)){
        habilitadorFlex = 1;
      }

      // Si estoy dentro del ciclo (habilitador = 1) y alcanzo un nuevo angulo mayor, se almacena este nuevo valor

      if ((habilitadorFlex==1)&&(Angulo_MayorFlex<=anguloFLEX)){
        Angulo_MayorFlex = anguloFLEX;
      }

      // Si el angulo es menor a 3 mientras estoy dentro del ciclo (habilitador =1), significa que acabó el ciclo
      // Se reinicia el habilitador y medidior de angulo mayor
      // Se verifica si el angulo mayor alcanzado en el ciclo supera o iguala al angulo meta y se actualizan las variables respectivas

      if ((anguloFLEX<3)&&(habilitadorFlex ==1)){
        if(Angulo_MayorFlex>=AnguloFlex.toInt()){
          Rep_ExitosasFlex = Rep_ExitosasFlex+1;
        }
        else{
          Rep_IncompletasFlex = Rep_IncompletasFlex+1;
        }
        habilitadorFlex = 0;
        Angulo_MayorFlex = 0;
      }

      // Se actualizan los iteradores

      tamanoFlex++;
      contadorFlex++;
     
      delay(25); // Frecuencia de muestre de 40Hz

      // Si pasaron 100 ms, se envía el dato a la app

      if (contadorFlex == 20){
        if  (anguloFLEX<0){
          anguloFLEX = 0;
        }
        
        anguloScreenFlex = map(anguloFLEX,0,AnguloFlex.toInt(),0,100); // Se mapea el angulo para que vaya de 0 al angulo meta a 0 a 100 para la pantalla y eso es lo que se envía a la app
         
        
        contadorFlex = 0;
        bluetoothSerial.println(anguloScreenFlex);
      }

      if (bluetoothSerial.available()>0){
        recibido = bluetoothSerial.read();
      }
    }

    // Si se recibe una 'd', significa que terminó el juego y se empieza con el almcenamiento de los datos en csv

    if (recibido == 'd'){
     // Serial.println("Comienza el conteo:");

      for (int j =0; j<tamanoFlex; j++){
        //Serial.println(numExtFlex[j]);
      }
      //Serial.println("\n");
     // Serial.println(tamanoFlex);


      // Abrir el archivo en modo escritura
      char myCharArray[19];
      IDFlex.toCharArray(myCharArray, 19); // Se pasa el nombre del documento a un array char porque ese es el formato que pide la biblioteca

      // Si ya existía un archivo con ese nombre, lo elimina

      //if (SD.exists(myCharArray)){
      //  SD.remove(myCharArray);
      //}

      dataFile = SD.open(myCharArray, FILE_WRITE);

      // Comprobar si se pudo abrir el archivo

      if (dataFile) { // Se escriben las primeras 2 filas
        dataFile.println("Nombre,Angulo,Torque,Maximo Angulo Alcanzado, Maxima Fuerza Alcanzada,Repeticiones Totales, Repeticiones Exitosas,ID del ejercicio");
        dataFile.println(nombreFlex+",0"+",0,"+String(anguloFlexMayor)+","+String(fuerzaFlexMayor)+","+String(Rep_ExitosasFlex+Rep_IncompletasFlex)+","+String(Rep_ExitosasFlex)+","+IDFlexDoc);

    // Se escriben los datos en las filas restantes
    for (int k =0; k<tamanoFlex; k++) {
      dataFile.println(","+String(numExtFlex[k])+","+String(fuerzaExtFlex[k]));
    }

    // Cerrar el archivo
    dataFile.close();
    //Serial.println("Archivo CSV creado con éxito");
  } 
    else {
    // Si no se pudo abrir el archivo, mostrar un mensaje de error
   // Serial.println("Error al abrir el archivo CSV");
  }

    }

// CALIBRACIÓN:

if (recibido == 'm'){
      contadorCal = 0;
}

while (recibido == 'm'){
      int data_cal = analogRead(LDR);

      contadorCal++;
      delay(25); // Frecuencia de muestre de 40Hz

      // Si pasaron 100 ms, se envía el dato a la app

      if (contadorCal == 20){
        bluetoothSerial.println(data_cal);
        contadorCal = 0;
      }

      if (bluetoothSerial.available()>0){
        recibido = bluetoothSerial.read();
      }
}

if (recibido == 'n') {
      habilitadorCal = 1;
      memset(receivedDataCal,0,6);
      ang_formula = "";
      v_formula = "";
    }

    // Si se recibe un 'o', indica que ya llegaron todos los caracteres del ID (Flex)
    // Se guardan todos los datos del array en una sola variable
    // Se desactiva el habilitador

    if (recibido == 'o'){
      habilitadorCal = 0;
      dataIndexCal = 0;

      for (int i = 0; i <2; i++){
        ang_formula = ang_formula +receivedDataCal[i];
      }

      for (int j = 2; j <6; j++){
        v_formula = v_formula +receivedDataCal[j];
      }


     // Serial.println(ang_formula);
     // Serial.println(v_formula);

      v_punto_formula = v_formula.toFloat();
      ang_punto_formula = ang_formula.toFloat();


    }

    // Si el habilitador está activo, entonces se guardan todos los datos recibidos en el array de ID (Flex)

    if ((habilitadorCal ==1) & (recibido != 'n')){
      receivedDataCal[dataIndexCal] = recibido;
      dataIndexCal++;
      //delay(100);
    }


// GENERAL:

// Si se recibe un 'x', indica que se ejercita el brazo derecho 
    if (recibido == 'p') {
      tipo_ej = 0;
     // Serial.println("FLEXION");
    }

    // Si se recibe un 'q', indica que se ejercita el brazo derecho 
    if (recibido == 'q') {
      tipo_ej = 1;
     // Serial.println("EXTENSION");
    }

 // Si se recibe un 'x', indica que se ejercita el brazo derecho 
    if (recibido == 'x') {
      identificador_brazo = 0;
     // Serial.println("BRAZO DERECHO");
    }

    // Si se recibe un 'y', indica que se ejercita el brazo izquierdo
    if (recibido == 'y') {
      identificador_brazo = 1;
    //  Serial.println("BRAZO IZQUIERDO");
    }

    // Si se recibe un 'g', indica que el siguiente caracter que viene es el número de resorte 
    // Se activa el habilitador

    if (recibido == 'g') {
          habilitadorResorte = 1;
          dataIndexResorte = 0;
          Resorte = "";
        }

    // Si se recibe un 'h', indica que ya llegó el caracter del resorte a utilizar
    // Se guardan todos los datos del array en una sola variable
    // Se desactiva el habilitador
    // Se establece el valor de la constante de elasticidad basado en cuál resorte se escogió (Cambiar cuando ya se tengan las constantes definidas)

    if (recibido == 'h'){
      habilitadorResorte = 0;
     // Serial.println("RESORTE:");
      for (int i = 0; i <1; i++){
        Resorte = Resorte +receivedDataResorte[i];
      }
      int Resorte_utilizar = Resorte.toInt();
      //Serial.println(Resorte); 
      if (Resorte_utilizar == 1) {
        k_resorte = 4030;
      } 
      else {
          k_resorte =4770;
      }

     // Serial.println("LA K:");
     // Serial.println(k_resorte);  

    }

    // Si el habilitador está activo, entonces se guarda el dato recibido del resorte

    if ((habilitadorResorte ==1) & (recibido != 'g')){
      receivedDataResorte[dataIndexResorte] = recibido;
      dataIndexResorte++;
      //delay(100);
    }
  

  }
}