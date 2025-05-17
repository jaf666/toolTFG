from SomeIPLab import MyLab

def main():    
    test = MyLab()
    a = test.start_someip_server(ecu_pair=("PCU_Proxy_Frontend", "IVC"), service_id=140)
    print(f"[RESULTADO] Éxito: {a[0]} | Comentario: {a[1]}")

if __name__ == "__main__":
    main()
