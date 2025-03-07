import os
from django.conf import settings
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import date
import io
from reportlab.lib.units import inch
from django.templatetags.static import static

def desenhar_elemento(canvas, y, elemento, x=50, espacamento=12):
    elemento.wrapOn(canvas, 500, 800)
    if isinstance(elemento, Paragraph):
        height = elemento.height
    elif isinstance(elemento, Table):
        height = elemento._height
    elif isinstance(elemento, Image):
        height = elemento.drawHeight  # Use drawHeight para Image
    else:
        height = 0  # Valor padrão para outros tipos de elementos

    if y - height < 50:
        canvas.showPage()
        y = 750
    elemento.drawOn(canvas, x, y - height)
    return y - height - espacamento

def gerar_contrato_pdf(pedido):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle(f"Contrato de Prestação de Serviços - Pedido {pedido.id}")

    styles = getSampleStyleSheet()

    # Estilo para títulos em negrito
    titulo_style = ParagraphStyle(
        name='TituloNegrito',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=16,
        alignment=0  # Alinhamento à esquerda
    )

    # Estilo para dados do cliente em negrito
    dados_cliente_style = ParagraphStyle(
        name='DadosClienteNegrito',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        alignment=0  # Alinhamento à esquerda
    )

    normal_style = styles['Normal']
    normal_style.alignment = 0  # Alinhamento à esquerda

    y = 750  # Posição inicial Y

    # Adicionar a logo da KQ
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'Logo KQ - azul.png')
    logo = Image(logo_path, width=2*inch, height=2*inch)
    y = desenhar_elemento(p, y, logo)

    # Dados do cliente
    dados_cliente = [
        "<br/>Dados do Cliente:<br/><br/>",
        f"Nome: {pedido.cliente.nome}<br/>",
        f"Email: {pedido.cliente.email}<br/>",
        f"Telefone: {pedido.cliente.telefone}<br/>",
        f"Endereço: {pedido.cliente.endereco}<br/>"
    ]
    dados_cliente_paragrafos = [Paragraph(dado, dados_cliente_style) for dado in dados_cliente]

    # Desenhar os dados do cliente
    for paragrafo in dados_cliente_paragrafos:
        y = desenhar_elemento(p, y, paragrafo)

    # Informações do contrato
    titulo_contrato = "<br/>CONTRATO DE FORNECIMENTO DE ARTIGOS PERSONALIZADOS<br/><br/>"
    titulo_contrato_paragrafo = Paragraph(titulo_contrato, titulo_style)
    y = desenhar_elemento(p, y, titulo_contrato_paragrafo)

    # Informações do contrato
    texto_contrato = [
        f"Pelo presente instrumento particular, de um lado, KQ PERSONALIZADOS LTDA, pessoa jurídica, inscrita no CNPJ/MF sob nº 28.819.632/0001-09, com sede na AV MAYAPAN 140, JARDIM PRIMAVERA, DUQUE DE CAXIAS - RJ, doravante denominada CONTRATADA, e, de outro lado, {pedido.cliente.nome}, doravante denominado CONTRATANTE, celebram o presente contrato de fornecimento de artigos personalizados, mediante as cláusulas e condições seguintes:<br/><br/>",
        f"<b>1. Objeto do Contrato</b><br/>O presente contrato tem por objeto o fornecimento de artigos personalizados pela CONTRATADA ao CONTRATANTE, conforme especificações detalhadas no pedido, que fará parte integrante deste contrato.<br/><br/>",
        f"<b>2. Especificações dos Artigos</b><br/>As especificações dos artigos personalizados, incluindo, mas não se limitando a, tipo de material, cores, tamanhos, estampas e demais detalhes, serão definidas no pedido, que deverá ser aprovado por ambas as partes.<br/><br/>",
        f"<b>3. Preço e Condições de Pagamento</b><br/>O preço total dos artigos personalizados será aquele especificado no pedido, que deverá ser aprovado pelo CONTRATANTE.<br/>As condições de pagamento serão as seguintes:<br/>50% do valor total no ato da encomenda, e o restante 50% na entrega dos artigos; ou<br/>100% do valor total no ato da encomenda.<br/><br/>",
        f"<b>4. Prazos</b><br/>O prazo para a entrega dos artigos personalizados será de 15 a 25 dias úteis, contados a partir da data da aprovação final do pedido e do recebimento do pagamento inicial (se aplicável). Qualquer prazo diferente deste deverá ser formalizado por e-mail.<br/><br/>",
        f"<b>5. Obrigações da CONTRATADA</b><br/>A CONTRATADA se obriga a fornecer os artigos personalizados de acordo com as especificações aprovadas no pedido, garantindo a qualidade dos materiais e a conformidade dos produtos.<br/>A CONTRATADA se responsabiliza por eventuais defeitos de fabricação nos artigos personalizados, desde que comunicados pelo CONTRATANTE no prazo de até 7 dias corridos a partir da data da entrega.<br/><br/>",
        f"<b>6. Obrigações do CONTRATANTE</b><br/>O CONTRATANTE se obriga a pagar o preço total dos artigos personalizados nas condições estabelecidas neste contrato.<br/>O CONTRATANTE se responsabiliza pela correta especificação dos artigos personalizados no pedido, incluindo tamanhos, cores e estampas.<br/><br/>",
        f"<b>7. Propriedade Intelectual</b><br/>A propriedade intelectual das estampas e designs fornecidos pelo CONTRATANTE permanecerá com este, sendo a CONTRATADA responsável apenas pela reprodução fiel das mesmas nos artigos personalizados.<br/>A CONTRATADA poderá utilizar os artigos personalizados produzidos para fins de divulgação de seu trabalho, desde que obtenha autorização expressa do CONTRATANTE.<br/><br/>",
        f"<b>8. Rescisão</b><br/>O presente contrato poderá ser rescindido por qualquer das partes, em caso de descumprimento das obrigações aqui estabelecidas.<br/>Em caso de rescisão por culpa da CONTRATADA, esta deverá restituir ao CONTRATANTE todos os valores pagos, acrescidos de multa de 10% sobre o valor já pago.<br/>Em caso de rescisão por culpa do CONTRATANTE, este perderá o valor pago, sem prejuízo de outras perdas e danos que a CONTRATADA possa comprovar.<br/><br/>",
        f"<b>9. Foro</b><br/>Fica eleito o foro da comarca de Duque de Caxias - RJ, para dirimir quaisquer dúvidas ou litígios decorrentes do presente contrato, com renúncia expressa a qualquer outro, por mais privilegiado que seja.<br/><br/>",
        f"DUQUE DE CAXIAS, {date.today().strftime('%d/%m/%Y')}<br/><br/>",
        f"_______________________________<br/>KQ PERSONALIZADOS LTDA<br/><br/>",
        f"_______________________________<br/>{pedido.cliente.nome}<br/>CONTRATANTE<br/><br/>"
    ]
    texto_contrato_paragrafos = [Paragraph(texto, normal_style) for texto in texto_contrato]

    # Desenhar o texto do contrato
    for paragrafo in texto_contrato_paragrafos:
        y = desenhar_elemento(p, y, paragrafo)

    # Adicionar informações do pedido e das ordens de serviço
    p.showPage()  # Adiciona uma nova página para as informações do pedido
    y = 750
    ptext = Paragraph("Informações do Pedido:\n\n", styles['Heading1'])
    y = desenhar_elemento(p, y, ptext)

    info_pedido = [
        f"Data do Pedido: {pedido.data_criacao.strftime('%d/%m/%Y %H:%M')}\n"
    ]

    for info in info_pedido:
        ptext = Paragraph(info, normal_style)
        y = desenhar_elemento(p, y, ptext)

    # Adicionar informações das ordens de serviço
    ptext = Paragraph("Ordens de Serviço:\n\n", styles['Heading1'])
    y = desenhar_elemento(p, y, ptext)

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
                y = desenhar_elemento(p, y, img, espacamento=2.5*inch)
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

        y = desenhar_elemento(p, y, t)

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

    y = desenhar_elemento(p, y, table)

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
