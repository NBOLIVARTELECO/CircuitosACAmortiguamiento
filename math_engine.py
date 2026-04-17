import numpy as np

class RLCCalculator:
    @staticmethod
    def calculate_series(R, L, C):
        """
        Calcula los parámetros para un circuito RLC en serie.
        R: Resistencia en Ohms
        L: Inductancia en Henrios
        C: Capacitancia en Faradios
        
        Retorna: omega_0, alpha, tipo_amortiguamiento
        """
        if L == 0 or C == 0:
            return 0, 0, "Error"
        
        omega_0 = 1 / np.sqrt(L * C)
        alpha = R / (2 * L)
        
        tipo = RLCCalculator._determinar_tipo(alpha, omega_0)
        return omega_0, alpha, tipo
        
    @staticmethod
    def calculate_parallel(R, L, C):
        """
        Calcula los parámetros para un circuito RLC en paralelo.
        """
        if L == 0 or C == 0 or R == 0:
            return 0, 0, "Error"
            
        omega_0 = 1 / np.sqrt(L * C)
        alpha = 1 / (2 * R * C)
        
        tipo = RLCCalculator._determinar_tipo(alpha, omega_0)
        return omega_0, alpha, tipo
        
    @staticmethod
    def _determinar_tipo(alpha, omega_0):
        # Usamos una pequeña tolerancia para errores de coma flotante
        if np.isclose(alpha, omega_0, rtol=1e-5):
            return "Críticamente Amortiguado"
        elif alpha > omega_0:
            return "Sobreamortiguado"
        else:
            return "Subamortiguado"

    @staticmethod
    def get_time_response(R, L, C, tipo_circuito, t_max=0.01, num_points=1000):
        """
        Genera los datos de la respuesta en el tiempo.
        Retorna: tiempos, valores_y
        """
        t = np.linspace(0, t_max, num_points)
        
        if tipo_circuito == "Serie":
            omega_0, alpha, tipo = RLCCalculator.calculate_series(R, L, C)
        else:
            omega_0, alpha, tipo = RLCCalculator.calculate_parallel(R, L, C)
            
        if tipo == "Error":
            return t, np.zeros_like(t)

        omega_d = np.sqrt(abs(omega_0**2 - alpha**2))
        
        # Condiciones iniciales arbitrarias para visualización: v(0) = 1, v'(0) = 0
        if tipo == "Subamortiguado":
            # A1 = 1, A2 = alpha/omega_d
            A1 = 1.0
            if omega_d != 0:
                A2 = alpha / omega_d
            else:
                A2 = 0
            y = np.exp(-alpha * t) * (A1 * np.cos(omega_d * t) + A2 * np.sin(omega_d * t))
            
        elif tipo == "Sobreamortiguado":
            s1 = -alpha + np.sqrt(alpha**2 - omega_0**2)
            s2 = -alpha - np.sqrt(alpha**2 - omega_0**2)
            # A1 + A2 = 1 => A1 = 1 - A2
            # s1*A1 + s2*A2 = 0 => s1*(1-A2) + s2*A2 = 0 => s1 + A2(s2 - s1) = 0 => A2 = -s1 / (s2 - s1)
            A2 = -s1 / (s2 - s1) if (s2 - s1) != 0 else 0
            A1 = 1.0 - A2
            y = A1 * np.exp(s1 * t) + A2 * np.exp(s2 * t)
            
        else: # Críticamente Amortiguado
            # A1 = 1, A2 = alpha
            A1 = 1.0
            A2 = alpha
            y = (A1 + A2 * t) * np.exp(-alpha * t)
            
        return t, y
