from django.conf import settings
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from datetime import date
import io
from reportlab.lib.units import inch

def gerar_contrato_pdf(pedido):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle(f"Contrato de Prestação de Serviços - Pedido {pedido.id}")

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    normal_style.alignment = 0  # Alinhamento à esquerda

    # Dados do cliente
    dados_cliente = [
        f"Dados do Cliente:\n",
        f"Nome: {pedido.cliente.nome}\n",
        f"Email: {pedido.cliente.email}\n",
        f"Telefone: {pedido.cliente.telefone}\n",
        f"Endereço: {pedido.cliente.endereco}\n"
    ]

    # Informações do contrato
    texto_contrato = [
        f"CONTRATO DE FORNECIMENTO DE ARTIGOS PERSONALIZADOS\n\n",
        f"Pelo presente instrumento particular, de um lado, KQ PERSONALIZADOS LTDA, pessoa jurídica, inscrita no CNPJ/MF sob nº [Número do CNPJ], com sede na AV MAYAPAN 140, JARDIM PRIMAVERA, DUQUE DE CAXIAS - RJ, doravante denominada CONTRATADA, e, de outro lado, {pedido.cliente.nome}, doravante denominado CONTRATANTE, celebram o presente contrato de fornecimento de artigos personalizados, mediante as cláusulas e condições seguintes:\n\n",
        f"1. Objeto do Contrato\nO presente contrato tem por objeto o fornecimento de artigos personalizados pela CONTRATADA ao CONTRATANTE, conforme especificações detalhadas no pedido, que fará parte integrante deste contrato.\n\n",
        f"2. Especificações dos Artigos\nAs especificações dos artigos personalizados, incluindo, mas não se limitando a, tipo de material, cores, tamanhos, estampas e demais detalhes, serão definidas no pedido, que deverá ser aprovado por ambas as partes.\n\n",
        f"3. Preço e Condições de Pagamento\nO preço total dos artigos personalizados será aquele especificado no pedido, que deverá ser aprovado pelo CONTRATANTE.\nAs condições de pagamento serão as seguintes:\n50% do valor total no ato da encomenda, e o restante 50% na entrega dos artigos; ou\n100% do valor total no ato da encomenda.\n\n",
        f"4. Prazos\nO prazo para a entrega dos artigos personalizados será de 15 a 25 dias úteis, contados a partir da data da aprovação final do pedido e do recebimento do pagamento inicial (se aplicável). Qualquer prazo diferente deste deverá ser formalizado por e-mail.\n\n",
        f"5. Obrigações da CONTRATADA\nA CONTRATADA se obriga a fornecer os artigos personalizados de acordo com as especificações aprovadas no pedido, garantindo a qualidade dos materiais e a conformidade dos produtos.\nA CONTRATADA se responsabiliza por eventuais defeitos de fabricação nos artigos personalizados, desde que comunicados pelo CONTRATANTE no prazo de até 7 dias corridos a partir da data da entrega.\n\n",
        f"6. Obrigações do CONTRATANTE\nO CONTRATANTE se obriga a pagar o preço total dos artigos personalizados nas condições estabelecidas neste contrato.\nO CONTRATANTE se responsabiliza pela correta especificação dos artigos personalizados no pedido, incluindo tamanhos, cores e estampas.\n\n",
        f"7. Propriedade Intelectual\nA propriedade intelectual das estampas e designs fornecidos pelo CONTRATANTE permanecerá com este, sendo a CONTRATADA responsável apenas pela reprodução fiel das mesmas nos artigos personalizados.\nA CONTRATADA poderá utilizar os artigos personalizados produzidos para fins de divulgação de seu trabalho, desde que obtenha autorização expressa do CONTRATANTE.\n\n",
        f"8. Rescisão\nO presente contrato poderá ser rescindido por qualquer das partes, em caso de descumprimento das obrigações aqui estabelecidas.\nEm caso de rescisão por culpa da CONTRATADA, esta deverá restituir ao CONTRATANTE todos os valores pagos, acrescidos de multa de 10% sobre o valor já pago.\nEm caso de rescisão por culpa do CONTRATANTE, este perderá o valor pago, sem prejuízo de outras perdas e danos que a CONTRATADA possa comprovar.\n\n",
        f"9. Foro\nFica eleito o foro da comarca de Duque de Caxias - RJ, para dirimir quaisquer dúvidas ou litígios decorrentes do presente contrato, com renúncia expressa a qualquer outro, por mais privilegiado que seja.\n\n",
        f"DUQUE DE CAXIAS, {date.today().strftime('%d/%m/%Y')}\n\n",
        f"_______________________________\nKQ PERSONALIZADOS LTDA\n\n",
        f"_______________________________\n{pedido.cliente.nome}\nCONTRATANTE\n\n"
    ]

    # Desenhar os dados do cliente
    y = 750  # Posição inicial Y
    for dado in dados_cliente:
        ptext = Paragraph(dado, normal_style)
        ptext.wrapOn(p, 500, 50)  # Largura máxima do parágrafo
        height = ptext.height
        if y - height < 50:  # Se não houver espaço suficiente na página
            p.showPage()  # Adiciona uma nova página
            y = 750  # Reinicia a posição Y
        ptext.drawOn(p, 50, y)
        y -= height + 12  # Ajustar a posição Y para o próximo parágrafo

    # Adicionar um espaçamento após os dados do cliente
    y -= 24  # Adiciona 24 pontos de espaçamento

    # Desenhar o texto do contrato
    for texto in texto_contrato:
        ptext = Paragraph(texto, normal_style)
        ptext.wrapOn(p, 500, 50)  # Largura máxima do parágrafo
        height = ptext.height
        if y - height < 50:  # Se não houver espaço suficiente na página
            p.showPage()  # Adiciona uma nova página
            y = 750  # Reinicia a posição Y
        ptext.drawOn(p, 50, y)
        y -= height + 12  # Ajustar a posição Y para o próximo parágrafo

    # Adicionar informações do pedido e das ordens de serviço
    p.showPage()  # Adiciona uma nova página para as informações do pedido
    y = 750
    ptext = Paragraph("Informações do Pedido:\n\n", styles['Heading1'])
    ptext.wrapOn(p, 500, 50)
    ptext.drawOn(p, 50, y)
    y -= ptext.height + 12

    info_pedido = [
        f"Data do Pedido: {pedido.data_criacao.strftime('%d/%m/%Y %H:%M')}\n"
    ]
#a tha é braba
    for info in info_pedido:
        ptext = Paragraph(info, normal_style)
        ptext.wrapOn(p, 500, 50)
        height = ptext.height
        if y - height < 50:
            p.showPage()
            y = 750
        ptext.drawOn(p, 50, y)
        y -= height + 12

    # Adicionar informações das ordens de serviço
    ptext = Paragraph("Ordens de Serviço:\n\n", styles['Heading1'])
    ptext.wrapOn(p, 500, 50)
    height = ptext.height
    if y - height < 50:
        p.showPage()
        y = 750
    ptext.drawOn(p, 50, y)
    y -= height + 12

    total_pedido = 0  # Inicializa o total do pedido

    # Dados para a tabela
    data = [["Produto", "Quantidade", "Valor Unitário", "Valor Total"]]

    for ordem in pedido.ordens_de_servico.all():
        total_quantidade = (
            ordem.pp_masculino + ordem.pp_feminino + ordem.p_masculino + ordem.p_feminino +
            ordem.m_masculino + ordem.m_feminino + ordem.g_masculino + ordem.g_feminino +
            ordem.gg_masculino + ordem.gg_feminino + ordem.xg_masculino + ordem.xg_feminino +
            ordem.esp_masculino + ordem.esp_feminino
        )
        valor_total = ordem.preco_unitario * total_quantidade
        total_pedido += valor_total  # Acumula o valor total

        data.append([
            ordem.produto.nome,
            str(total_quantidade),
            f"R$ {ordem.preco_unitario:.2f}",
            f"R$ {valor_total:.2f}"
        ])

        # Adicionar mockup (se existir)
        if ordem.mockup:
            try:
                img = Image(ordem.mockup.path, width=2*inch, height=2*inch)
                # Ajustar a posição Y para o mockup
                if y - 2.5*inch < 50:
                    p.showPage()
                    y = 750
                img.drawOn(p, 50, y - 2*inch)
                y -= 2.5*inch  # Ajustar a posição Y após a imagem
            except Exception as e:
                print(f"Erro ao adicionar imagem: {e}")

        # Adicionar grade de tamanhos em formato de tabela
        tamanho_data = [
            ["Tamanho", "Masculino", "Feminino"],
            ["PP", str(ordem.pp_masculino), str(ordem.pp_feminino)],
            ["P", str(ordem.p_masculino), str(ordem.p_feminino)],
            ["M", str(ordem.m_masculino), str(ordem.m_feminino)],
            ["G", str(ordem.g_masculino), str(ordem.g_feminino)],
            ["GG", str(ordem.gg_masculino), str(ordem.gg_feminino)],
            ["XG", str(ordem.xg_masculino), str(ordem.xg_feminino)],
            ["Especial", str(ordem.esp_masculino), str(ordem.esp_feminino)],
        ]

        t = Table(tamanho_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))

        # Use wrapOn para calcular a altura da tabela
        t.wrapOn(p, 500, 50)
        table_height = t._height  # Obtenha a altura da tabela

        # Ajustar a posição Y para a tabela
        if y - table_height < 50:
            p.showPage()
            y = 750
        t.drawOn(p, 50, y)
        y -= table_height + 12

        # Adicionar um espaçamento após a tabela
        y -= 24  # Adiciona 24 pontos de espaçamento

    # Adicionar frete e total
    data.append(["", "", "Frete:", f"R$ {pedido.frete:.2f}"])
    total_com_frete = total_pedido + pedido.frete
    data.append(["", "", "Total:", f"R$ {total_com_frete:.2f}"])

    # Criar tabela
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))

    # Use wrapOn para calcular a altura da tabela
    table.wrapOn(p, 500, 50)
    table_height = table._height  # Obtenha a altura da tabela

    # Ajustar a posição Y para a tabela
    if y - table_height < 50:
        p.showPage()
        y = 750
    table.drawOn(p, 50, y)
    y -= table_height + 12

    p.showPage()
    p.save()
    pdf_file = buffer.getvalue()
    return pdf_file

def enviar_contrato_email(pedido, pdf_file):
    subject = f'Contrato de Prestação de Serviços - Pedido {pedido.id}'
    message = f'Prezado(a) {pedido.cliente.nome},\n\nSegue em anexo o contrato de prestação de serviços referente ao seu pedido {pedido.id}.\n\nAtenciosamente,\n[Nome da Sua Empresa]'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [pedido.cliente.email]

    email = EmailMessage(subject, message, from_email, to_email)
    email.attach(f'contrato_pedido_{pedido.id}.pdf', pdf_file, 'application/pdf')
    email.send()
