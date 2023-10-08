import serial
import time
import SD  # Asegúrate de tener la biblioteca SD instalada

# Configuración de la comunicación serie
ser = serial.Serial('COMX', 9600)  # Cambia 'COMX' al puerto serie correcto en tu sistema

# Importación de bibliotecas
File dataFile  # Variable para archivos csv
int contadorCal  # Variable para calibración
char receivedDataCal[6]  # Array para guardar los datos recibidos de calibración
int habilitadorCal = 0
String ang_formula
String v_formula
int dataIndexCal = 0
int tipo_ej = 0  # 0 es para flexión

float pendiente_formula = 0.2469
float v_punto_formula = 0
float ang_punto_formula = -149.08

int LDR = A6  # Pin para medir pot (14)
float k_resorte = 1  # Número de resorte a utilizar
char receivedDataResorte[1]
int dataIndexResorte = 0
int habilitadorResorte = 0
String Resorte
int identificador_brazo = 0
char letra = 'F'

# Variables de flexión
int numExtFlex[12000]  # Array para guardar los datos de ángulo de extensión y flexión
float fuerzaExtFlex[10000]  # Array para guardar los datos de fuerza asociada a la extensión y flexión
int contadorFlex = 0  # Contador para saber "cuándo" enviar los datos para la actualización del carro en el juego
int anguloFlexMayor = 0  # Ángulo de flexión máximo alcanzado
float fuerzaFlexMayor = 0  # Fuerza flexión máxima alcanzada
char receivedDataIDFlex[18]  # Datos recibidos de la ID de la persona para flexión
char receivedDataNombreFlex[255]  # Datos recibidos del nombre de la persona
int dataIndexIDFlex = 0  # Iterador para guardar los datos del ID en el array correspondiente
int dataIndexNombreFlex = 0  # Iterador guardar los datos del nombre en el array correspondiente
int habilitadorCedulaFlex = 0  #  Habilitador para saber cuándo empezar a guardar los datos del ID y cuándo terminar
int habilitadorNombreFlex = 0  #  Habilitador para saber cuándo empezar a guardar los datos del nombre y cuándo terminar
String nombreFlex  # Aquí se almacenan los caracteres del array de nombre concatenados en una sola variable
String IDFlex  # Aquí se almacena el ID concatenado con el que se guardará el documento csv
String IDFlexDoc  # Código del ejercicio que irá en el documento (0 para flexión)
int tamanoFlex = 0  # Iterador para guardar los datos de ángulo de flexión en el array. También se utiliza como iterador para el array de fuerza
int Angulo_MayorFlex = 0  # Variable para saber si en cada ciclo de ejercicio se alcanzó el ángulo meta
int Rep_ExitosasFlex = 0  # Para contar las repeticiones exitosas de flexión
int Rep_IncompletasFlex = 0  # Para contar las repeticiones incompletas de flexión
int habilitadorFlex = 0  # Indica cuándo comienza una nueva repetición de flexión
char receivedDataAnguloFlex[2]  # Para almacenar el ángulo meta
int dataIndexAnguloFlex = 0  # Iterador para guardar los datos de ángulo meta en el array
int habilitadorAnguloFlex = 0  # Habilitador para saber cuándo empezar a guardar los datos de ángulo meta y cuándo terminar
String AnguloFlex  # Almacena los valores concatenados del ángulo meta guardado en el array
int anguloScreenFlex

def setup():
  Serial.begin(38400)  # Inicializar el puerto serial para la comunicación con la computadora
  bluetoothSerial.begin(9600)  # Inicializar el puerto serial para el módulo Bluetooth HC-05
  pinMode(LDR, INPUT)  # Pin 14 como entrada

  # Inicializar la tarjeta SD
  if not SD.begin(BUILTIN_SDCARD):
    Serial.println("Error al iniciar la tarjeta SD")

def loop():
  if bluetoothSerial.available():
    char recibido = bluetoothSerial.read()  # Leer el primer carácter recibido

    # PARA FLEXIÓN:

    # Si se recibe un 'a', indica que los siguientes caracteres que vienen son el ID (flex)
    # Se activa el habilitador

    if recibido == 'a':
      habilitadorCedulaFlex = 1
      dataIndexIDFlex = 0
      IDFlex = ""

    # Si se recibe un 'b', indica que ya llegaron todos los caracteres del ID (Flex)
    # Se guardan todos los datos del array en una sola variable
    # Se desactiva el habilitador

    if recibido == 'b':
      char brazo = 'D'
      if tipo_ej == 0:
        IDFlexDoc = "0"  # 0 para flexion
        letra = 'F'
      else:
        IDFlexDoc = "1"
        letra = 'E'

      if identificador_brazo == 0:
        brazo = 'D'  # 0 para derecho
      else:
        brazo = 'I'
      habilitadorCedulaFlex = 0
      Serial.println("ID:")
      receivedDataIDFlex[12] = brazo
      receivedDataIDFlex[13] = letra  # Se agrega una como distintivo de flexión
      receivedDataIDFlex[14] = '.'
      receivedDataIDFlex[15] = 'c'
      receivedDataIDFlex[16] = 's'
      receivedDataIDFlex[17] = 'v'

      for int i in range(18):
        IDFlex = IDFlex + receivedDataIDFlex[i]

      Serial.println(IDFlex)
      Serial.println(IDFlexDoc)

    # Si el habilitador está activo, entonces se guardan todos los datos recibidos en el array de ID (Flex)

    if habilitadorCedulaFlex == 1 and recibido != 'a':
      receivedDataIDFlex[dataIndexIDFlex] = recibido
      dataIndexIDFlex++
      #delay(100)

    # Si se recibe un 'e', indica que los siguientes caracteres que vienen son el ángulo meta (Flex)
    # Se activa el habilitador

    if recibido == 'e':
      habilitadorAnguloFlex = 1
      dataIndexAnguloFlex = 0
      AnguloFlex = ""

    # Si se recibe un 'f', indica que ya llegaron todos los caracteres del ángulo meta (Flex)
    # Se guardan todos los datos del array en una sola variable
    # Se desactiva el habilitador

    if recibido == 'f':
      habilitadorAnguloFlex = 0

      for int i in range(2):
        AnguloFlex = AnguloFlex + receivedDataAnguloFlex[i]
      Serial.println("ANGULO:")
      Serial.println(AnguloFlex)

    # Si el habilitador está activo, entonces se guardan todos los datos recibidos en el array de ángulo meta (Flex)

    if habilitadorAnguloFlex == 1 and recibido != 'e':
      receivedDataAnguloFlex[dataIndexAnguloFlex] = recibido
      dataIndexAnguloFlex++
      #delay(100)

    # Si se recibe un '*', indica que los siguientes caracteres que vienen son el nombre (Flex)
    # Se activa el habilitador

    if recibido == '*':
      Serial.println("NOMBRE:")
      habilitadorNombreFlex = 1
      habilitadorCedulaFlex = 0
      dataIndexNombreFlex = 0
      nombreFlex = ""

    # Si se recibe un '+', indica que ya llegaron todos los caracteres del nombre (Flex)
    # Se guardan todos los datos del array en una sola variable
    # Se desactiva el habilitador

    if recibido == '+':
      habilitadorNombreFlex = 0
      Serial.println("AHORA NOMBRE:")
      for int i in range(dataIndexNombreFlex):
        nombreFlex = nombreFlex + receivedDataNombreFlex[i]
      Serial.println(nombreFlex)

    # Si el habilitador está activo, entonces se guardan todos los datos recibidos en el array de nombre (Flex)

    if habilitadorNombreFlex == 1 and recibido != '*':
      Serial.println(dataIndexNombreFlex)
      receivedDataNombreFlex[dataIndexNombreFlex] = recibido
      dataIndexNombreFlex++

    # Si se recibe un 'c', indica que se está en el juego de flexión
    # Se ponen todos los iteradores en 0

    if recibido == 'c':
      memset(numExtFlex, 0, tamanoFlex)
      memset(numExtFlex, 0, tamanoFlex)
      contadorFlex = 0
      tamanoFlex = 0
      Serial.println("OPCIONES:")
      Serial.println(identificador_brazo)
      Serial.println(tipo_ej)

    # Mientras el último recibido sea 'c', se envían los datos a la app y se almacenan en un array
    # Se calcula el valor de fuerza
    # Se cuentan cuántas repeticiones fueron correctas e incorrectas

    while recibido == 'c':
      int data = analogRead(LDR)
      int anguloFLEX
      #Serial.println("OPCIONES:")
      #Serial.println(identificador_brazo)
      #Serial.println(tipo_ej)

      #delay(2000)
      if identificador_brazo == 0 and tipo_ej == 0:
        anguloFLEX = pendiente_formula * (data - v_punto_formula) + ang_punto_formula  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
      elif identificador_brazo == 1 and tipo_ej == 0:
        anguloFLEX = -(pendiente_formula * (data - v_punto_formula) + ang_punto_formula)  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
      elif identificador_brazo == 0 and tipo_ej == 1:
        anguloFLEX = -(pendiente_formula * (data - v_punto_formula) + ang_punto_formula)  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
      elif identificador_brazo == 1 and tipo_ej == 1:
        anguloFLEX = (pendiente_formula * (data - v_punto_formula) + ang_punto_formula)  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
      Serial.println(anguloFLEX)

      float fuerzaF = k_resorte * 37.3823e-6 * anguloFLEX
      numExtFlex[tamanoFlex] = anguloFLEX
      fuerzaExtFlex[tamanoFlex] = fuerzaF

      if anguloFLEX >= anguloFlexMayor:
        anguloFlexMayor = anguloFLEX

      if fuerzaF >= fuerzaFlexMayor:
        fuerzaFlexMayor = fuerzaF

      # Si el ángulo es mayor a 3 y el habilitador es 0, se comienza un nuevo ciclo de ejercicio

      if anguloFLEX > 3 and habilitadorFlex == 0:
        habilitadorFlex = 1

      # Si estoy dentro del ciclo (habilitador = 1) y alcanzo un nuevo ángulo mayor, se almacena este nuevo valor

      if habilitadorFlex == 1 and Angulo_MayorFlex <= anguloFLEX:
        Angulo_MayorFlex = anguloFLEX

      # Si el ángulo es menor a 3 mientras estoy dentro del ciclo (habilitador = 1), entonces cuento una repetición exitosa

      if anguloFLEX < 3 and habilitadorFlex == 1:
        habilitadorFlex = 0
        contadorFlex++
        Rep_ExitosasFlex++
        Serial.println("REPETICIÓN CORRECTA")

      # Si el ángulo es mayor a 0 y menor a 3 mientras estoy dentro del ciclo (habilitador = 1), entonces cuento una repetición incompleta

      if anguloFLEX > 0 and anguloFLEX < 3 and habilitadorFlex == 1:
        habilitadorFlex = 0
        contadorFlex++
        Rep_IncompletasFlex++
        Serial.println("REPETICIÓN INCOMPLETA")

      // Serial.println("COUNT FLEX: ");
      // Serial.println(contadorFlex);
      // Serial.println("MAYOR ANGULO:");
      // Serial.println(anguloFlexMayor);

      // Si se recibe un 'g', indica que el juego de flexión terminó
      // Se desactiva el habilitador

      if recibido == 'g':
        habilitadorFlex = 0
        tamanoFlex = contadorFlex
        Serial.println("El juego de flexión ha terminado")
        Serial.println("COUNT FLEX: ");
        Serial.println(contadorFlex);
        Serial.println("MAYOR ANGULO:");
        Serial.println(anguloFlexMayor);
        Serial.println("MAYOR FUERZA:");
        Serial.println(fuerzaFlexMayor);

        for int i in range(tamanoFlex):
          Serial.print(numExtFlex[i])
          Serial.print("   ")
          Serial.println(fuerzaExtFlex[i])

        //Serial.println("FUERZA FLEX: ");
        //Serial.println(fuerzaF);

      //delay(1000)

      // if (digitalRead(electricoFlex) == HIGH) {
      //     digitalWrite(electricoFlex, LOW);
      // }

      // if (digitalRead(electricoFlex) == LOW) {
      //     digitalWrite(electricoFlex, HIGH);
      // }

      // digitalWrite(electricoFlex, HIGH);
      //delay(100);

      // Si se recibe un 'g', indica que el juego de flexión terminó
      // Se desactiva el habilitador

      if recibido == 'g':
        habilitadorFlex = 0
        tamanoFlex = contadorFlex
        Serial.println("El juego de flexión ha terminado")
        Serial.println("COUNT FLEX: ");
        Serial.println(contadorFlex);
        Serial.println("MAYOR ANGULO:");
        Serial.println(anguloFlexMayor);
        Serial.println("MAYOR FUERZA:");
        Serial.println(fuerzaFlexMayor);

        for int i in range(tamanoFlex):
          Serial.print(numExtFlex[i])
          Serial.print("   ")
          Serial.println(fuerzaExtFlex[i])

        //Serial.println("FUERZA FLEX: ");
        //Serial.println(fuerzaF);

      //delay(1000)

      // if (digitalRead(electricoFlex) == HIGH) {
      //     digitalWrite(electricoFlex, LOW);
      // }

      // if (digitalRead(electricoFlex) == LOW) {
      //     digitalWrite(electricoFlex, HIGH);
      // }

      // digitalWrite(electricoFlex, HIGH);
      //delay(100);

    # PARA CALIBRACIÓN:

    # Si se recibe un 'i', indica que se está en la calibración
    # Se ponen todos los iteradores en 0

    if recibido == 'i':
      memset(receivedDataCal, 0, 6)
      contadorCal = 0
      dataIndexCal = 0
      habilitadorCal = 0
      Serial.println("HabilitadorCal: ");
      Serial.println(habilitadorCal)

    # Mientras el último recibido sea 'i', se envían los datos a la app y se almacenan en un array
    # Se calcula el valor de ángulo
    # Se cuentan cuántas veces se pasó por cada ángulo

    while recibido == 'i':
      int data = analogRead(LDR)
      float anguloCal

      if identificador_brazo == 0 and tipo_ej == 0:
        anguloCal = pendiente_formula * (data - v_punto_formula) + ang_punto_formula  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
      elif identificador_brazo == 1 and tipo_ej == 0:
        anguloCal = -(pendiente_formula * (data - v_punto_formula) + ang_punto_formula)  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
      elif identificador_brazo == 0 and tipo_ej == 1:
        anguloCal = -(pendiente_formula * (data - v_punto_formula) + ang_punto_formula)  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
      elif identificador_brazo == 1 and tipo_ej == 1:
        anguloCal = (pendiente_formula * (data - v_punto_formula) + ang_punto_formula)  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE

      float anguloCal1 = float(int(anguloCal * 10)) / 10

      // Si se recibe un 'i', indica que se está en la calibración
      // Se ponen todos los iteradores en 0

      if recibido == 'i':
        memset(receivedDataCal, 0, 6)
        contadorCal = 0
        dataIndexCal = 0
        habilitadorCal = 0
        Serial.println("HabilitadorCal: ");
        Serial.println(habilitadorCal)

      // Mientras el último recibido sea 'i', se envían los datos a la app y se almacenan en un array
      // Se calcula el valor de ángulo
      // Se cuentan cuántas veces se pasó por cada ángulo

      while recibido == 'i':
        int data = analogRead(LDR)
        float anguloCal

        if identificador_brazo == 0 and tipo_ej == 0:
          anguloCal = pendiente_formula * (data - v_punto_formula) + ang_punto_formula  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
        elif identificador_brazo == 1 and tipo_ej == 0:
          anguloCal = -(pendiente_formula * (data - v_punto_formula) + ang_punto_formula)  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
        elif identificador_brazo == 0 and tipo_ej == 1:
          anguloCal = -(pendiente_formula * (data - v_punto_formula) + ang_punto_formula)  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE
        elif identificador_brazo == 1 and tipo_ej == 1:
          anguloCal = (pendiente_formula * (data - v_punto_formula) + ang_punto_formula)  # CAMBIAR POR LA FORMULA DE PUNTO PENDIENTE

        float anguloCal1 = float(int(anguloCal * 10)) / 10

        // Si el habilitador está desactivado y se recibe un número entre 0 y 9 (inclusive), se activa el habilitador y se guarda el número en el array

        if habilitadorCal == 0 and recibido >= '0' and recibido <= '9':
          habilitadorCal = 1
          receivedDataCal[dataIndexCal] = recibido
          dataIndexCal++

        // Si el habilitador está activado y se recibe un número entre 0 y 9 (inclusive), se guarda el número en el array

        elif habilitadorCal == 1 and recibido >= '0' and recibido <= '9':
          receivedDataCal[dataIndexCal] = recibido
          dataIndexCal++

        // Si el habilitador está activado y se recibe una coma, se calcula el valor de ángulo

        elif habilitadorCal == 1 and recibido == ',':
          habilitadorCal = 0
          int anguloCalibracion = 0

          for int i in range(dataIndexCal):
            anguloCalibracion = anguloCalibracion * 10 + (receivedDataCal[i] - '0')

          // Si el ángulo es mayor a 0 y menor a 3, se suma 1 al contador de ángulos

          if anguloCal1 > 0 and anguloCal1 < 3:
            ang_formula = ang_formula + anguloCal1 + ","

          // Si el ángulo es igual a 0, se suma 1 al contador de ángulos

          elif anguloCal1 == 0:
            ang_formula = ang_formula + anguloCal1 + ","

          // Si el ángulo es mayor a 3, se suma 1 al contador de ángulos

          elif anguloCal1 > 3:
            ang_formula = ang_formula + anguloCal1 + ","
            contadorCal++

          Serial.println("COUNT CAL: ");
          Serial.println(contadorCal);

        // Si se recibe un 'j', indica que el juego de calibración terminó
        // Se desactiva el habilitador

        if recibido == 'j':
          habilitadorCal = 0
          Serial.println("El juego de calibración ha terminado")
          ang_formula = ang_formula + ".c" + identificador_brazo + "-" + letra + ".csv"
          //Serial.println(ang_formula);
          File dataFile = SD.open(ang_formula, FILE_WRITE);

          if (dataFile) {
            dataFile.print("Ángulo de calibración (grados): ");
            dataFile.println();
            dataFile.print(ang_formula);
            dataFile.print("Ángulo (grados)");
            dataFile.print(",");
            dataFile.print("LDR");
            dataFile.print(",");
            dataFile.println();

            for int i in range(dataIndexCal):
              dataFile.print(anguloCalibracion);
              dataFile.print(",");
              dataFile.print(ang_formula);
              dataFile.print(",");
              dataFile.println();
          }
          dataFile.close();
          //delay(1000);

          # PARA RESORTE:

          # Si se recibe un 'k', indica que se está en el juego de resorte
          # Se ponen todos los iteradores en 0

          if recibido == 'k':
            memset(receivedDataResorte, 0, 1)
            habilitadorResorte = 0
            dataIndexResorte = 0
            Serial.println("HabilitadorResorte: ");
            Serial.println(habilitadorResorte)

          # Mientras el último recibido sea 'k', se envían los datos a la app y se almacenan en un array

          while recibido == 'k':
            int data = analogRead(LDR)

            // Si el habilitador está desactivado y se recibe un número entre 0 y 9 (inclusive), se activa el habilitador y se guarda el número en el array

            if habilitadorResorte == 0 and recibido >= '0' and recibido <= '9':
              habilitadorResorte = 1
              receivedDataResorte[dataIndexResorte] = recibido
              dataIndexResorte++

            # Si el habilitador está activado y se recibe un número entre 0 y 9 (inclusive), se guarda el número en el array

            elif habilitadorResorte == 1 and recibido >= '0' and recibido <= '9':
              receivedDataResorte[dataIndexResorte] = recibido
              dataIndexResorte++

            # Si el habilitador está activado y se recibe una coma, se calcula el valor de fuerza

            elif habilitadorResorte == 1 and recibido == ',':
              habilitadorResorte = 0
              int fuerzaResorte = 0

              for int i in range(dataIndexResorte):
                fuerzaResorte = fuerzaResorte * 10 + (receivedDataResorte[i] - '0')

              fuerzaResorte = fuerzaResorte - 72

              // Si la fuerza es mayor a 0 y menor a 4, se suma 1 al contador de fuerza

              if fuerzaResorte > 0 and fuerzaResorte < 4:
                fuerza_formula = fuerza_formula + fuerzaResorte + ","
                print("COUNT RESORTE: ")
                print(fuerza_formula);

              // Si se recibe un 'l', indica que el juego de resorte terminó
              // Se desactiva el habilitador

              if recibido == 'l':
                Serial.println("El juego de resorte ha terminado")
                fuerza_formula = fuerza_formula + ".c" + identificador_brazo + "-" + letra + ".csv"
                print(fuerza_formula)
                File dataFile = SD.open(fuerza_formula, FILE_WRITE);

                if (dataFile) {
                  dataFile.print("Fuerza de resorte (kN/m): ");
                  dataFile.println();
                  dataFile.print(fuerza_formula);
                  dataFile.print("Fuerza (kN)");
                  dataFile.print(",");
                  dataFile.print("LDR");
                  dataFile.print(",");
                  dataFile.println();

                  for int i in range(dataIndexResorte):
                    dataFile.print(fuerzaResorte);
                    dataFile.print(",");
                    dataFile.print(fuerza_formula);
                    dataFile.print(",");
                    dataFile.println();
                }
                dataFile.close();
                //delay(1000);

# Función para convertir un arreglo de caracteres a una cadena
String charArrayToString(char array[], int size):
  String result = ""
  for int i in range(size):
    result += array[i]
  return result

# Función para guardar los datos en un archivo CSV
void saveDataToCSV(String fileName, String data):
  File dataFile = SD.open(fileName, FILE_WRITE)
  if (dataFile):
    dataFile.println(data)
    dataFile.close()
  else:
    Serial.println("Error al abrir el archivo")