const PDFDocument = require("pdfkit");
const fs = require("fs");

module.exports = (sale) => new Promise(resolve => {
  const file = `receipt-${sale.id}.pdf`;
  const doc = new PDFDocument({ size: "A6", margin: 10 });
  doc.pipe(fs.createWriteStream(file));

  doc.text("DO‘KON NOMI");
  doc.text("Manzil");
  doc.text(`Sana: ${new Date().toLocaleString()}`);
  doc.text(`Sotuvchi: ${sale.user}`);
  doc.text("----------------");
  doc.text(`JAMI: ${sale.total} so‘m`);
  if (sale.discount) doc.text(`Chegirma: ${sale.discount} so‘m`);

  doc.end();
  resolve(file);
});
