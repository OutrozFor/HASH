import csv
import random

class TabelaHashCPF:
    def __init__(self, tamanho_inicial=1000, funcao_hash=None):
        """
        Tabela hash especializada para eliminar duplicatas por CPF.
        Permite passar uma função de hash customizada.
        """
        self.tamanho = self._proximo_primo(tamanho_inicial)
        self.tabela = [[] for _ in range(self.tamanho)]
        self.contador = 0
        self.colisoes = 0
        # Permite função de hash customizada
        self.funcao_hash = funcao_hash if funcao_hash else self._hash_cpf

    @staticmethod
    def _proximo_primo(n):
        if n <= 1:
            return 2
        primo = n
        while True:
            if all(primo % i != 0 for i in range(2, int(primo**0.5) + 1)):
                return primo
            primo += 1

    def _hash_cpf(self, cpf):
        cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
        if len(cpf_limpo) != 11:
            raise ValueError("CPF deve conter 11 dígitos")
        cpf_int = int(cpf_limpo)
        # Método de multiplicação com constante de Knuth
        ''' o método de multiplicação é uma tecnica de hashing que utiliza
        uma constante irracional (como a raiz quadrada de 5) para distribuit'''
        A = (5**0.5 - 1)/2
        hash_val = int(self.tamanho * ((cpf_int * A) % 1))
        return hash_val

    def inserir_cliente(self, cliente):
        cpf = cliente['cpf']
        indice = self.funcao_hash(cpf)
        lista = self.tabela[indice]
        for cliente_existente in lista:
            if cliente_existente['cpf'] == cpf:
                return False  # Cliente duplicado
        lista.append(cliente)
        self.contador += 1
        if len(lista) > 1:
            self.colisoes += 1
        if self.fator_carga() > 0.7:
            self._redimensionar()
        return True

    def buscar_cliente(self, cpf):
        """Busca um cliente pelo CPF."""
        indice = self.funcao_hash(cpf)
        lista = self.tabela[indice]
        for cliente in lista:
            if cliente['cpf'] == cpf:
                return cliente
        return None

    def remover_cliente(self, cpf):
        """Remove um cliente pelo CPF."""
        indice = self.funcao_hash(cpf)
        lista = self.tabela[indice]
        for i, cliente in enumerate(lista):
            if cliente['cpf'] == cpf:
                del lista[i]
                self.contador -= 1
                return True
        return False

    def __getitem__(self, indice):
        """Permite acesso por índice (bucket)."""
        return self.tabela[indice]

    def fator_carga(self):
        return self.contador / self.tamanho

    def _redimensionar(self):
        nova_tamanho = self._proximo_primo(self.tamanho * 2)
        nova_tabela = TabelaHashCPF(tamanho_inicial=nova_tamanho, funcao_hash=self.funcao_hash)
        for bucket in self.tabela:
            for cliente in bucket:
                nova_tabela.inserir_cliente(cliente)
        self.tamanho = nova_tabela.tamanho
        self.tabela = nova_tabela.tabela
        self.colisoes = nova_tabela.colisoes

    def get_clientes_unicos(self):
        clientes = []
        for bucket in self.tabela:
            clientes.extend(bucket)
        return clientes

    def __len__(self):
        return self.contador

    def estatisticas(self):
        return {
            'tamanho_tabela': self.tamanho,
            'clientes_unicos': self.contador,
            'colisoes': self.colisoes,
            'fator_carga': self.fator_carga(),
            'media_por_bucket': self.contador / self.tamanho
        }

def gerar_cpf_aleatorio():
    """Gera um CPF válido aleatório para testes."""
    def calcula_digito(cpf_base):
        soma = 0
        for i, digito in enumerate(cpf_base):
            soma += int(digito) * (len(cpf_base) + 1 - i)
        resto = soma % 11
        return '0' if resto < 2 else str(11 - resto)
    
    cpf_base = [str(random.randint(0, 9)) for _ in range(9)]
    cpf_base.append(calcula_digito(cpf_base))
    cpf_base.append(calcula_digito(cpf_base[:10]))
    
    return ''.join(cpf_base[:3]) + '.' + ''.join(cpf_base[3:6]) + '.' + ''.join(cpf_base[6:9]) + '-' + ''.join(cpf_base[9:])


def criar_dataset_teste(n_clientes=1000, duplicatas=0.1):
    """
    Cria um dataset de teste com clientes, incluindo algumas duplicatas.
    
    Args:
        n_clientes: Número total de registros a gerar.
        duplicatas: Percentual de registros que devem ser duplicatas (0.0 a 1.0).
        
    Returns:
        Lista de dicionários representando clientes.
    """
    n_unicos = int(n_clientes * (1 - duplicatas))
    clientes_unicos = []
    
    # Gera clientes únicos
    for _ in range(n_unicos):
        cpf = gerar_cpf_aleatorio()
        clientes_unicos.append({
            'cpf': cpf,
            'nome': f'Cliente_{random.randint(1, 100000)}',
            'idade': random.randint(18, 90),
            'cidade': random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Porto Alegre'])
        })
    
    # Cria duplicatas
    dataset = clientes_unicos.copy()
    for _ in range(n_clientes - n_unicos):
        cliente = random.choice(clientes_unicos).copy()
        # Modifica alguns campos mas mantém o CPF
        cliente['nome'] = f"Duplicata_{cliente['nome']}"
        dataset.append(cliente)
    
    random.shuffle(dataset)
    return dataset


def processar_dataset(dataset):
    """Processa o dataset removendo duplicatas usando a tabela hash."""
    tabela = TabelaHashCPF()
    registros_totais = len(dataset)
    
    for cliente in dataset:
        tabela.inserir_cliente(cliente)
    
    stats = tabela.estatisticas()
    stats['registros_totais'] = registros_totais
    stats['duplicatas_removidas'] = registros_totais - len(tabela)
    
    return tabela.get_clientes_unicos(), stats


def salvar_csv(clientes, arquivo_saida):
    """Salva a lista de clientes em um arquivo CSV."""
    campos = ['cpf', 'nome', 'idade', 'cidade']
    
    with open(arquivo_saida, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(clientes)


if __name__ == "__main__":
    '''
    script principal para criar e processar um dataset de teste
    '''
    # Cria e processa dataset de exemplo
    print("Criando dataset de teste com 10.000 clientes (10% duplicatas)...")
    dataset = criar_dataset_teste(n_clientes=10000, duplicatas=0.1)
    
    print("Processando para remover duplicatas...")
    clientes_unicos, estatisticas = processar_dataset(dataset)
    
    print("\nEstatísticas do processamento:")
    print(f"Registros totais: {estatisticas['registros_totais']}")
    print(f"Clientes únicos: {estatisticas['clientes_unicos']}")
    print(f"Duplicatas removidas: {estatisticas['duplicatas_removidas']}")
    print(f"Colisões ocorridas: {estatisticas['colisoes']}")
    print(f"Fator de carga final: {estatisticas['fator_carga']:.2f}")
    print(f"Média por bucket: {estatisticas['media_por_bucket']:.2f}")
    
    # Salva resultados
    print("\nSalvando clientes únicos em 'clientes_unicos.csv'...")
    salvar_csv(clientes_unicos, 'clientes_unicos.csv')
    
    print("Processo concluído!")