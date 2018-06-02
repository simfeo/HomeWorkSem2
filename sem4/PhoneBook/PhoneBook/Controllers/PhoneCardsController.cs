﻿using System;
using System.Collections.Generic;
using System.Data;
using System.Data.Entity;
using System.Linq;
using System.Net;
using System.Web;
using System.Web.Mvc;
using PhoneBook.Models;

namespace PhoneBook.Controllers
{
    public class PhoneCardsController : Controller
    {
        private PhoneCardDBContext db = new PhoneCardDBContext();

        // GET: PhoneCards
        public ActionResult Index()
        {
            return View(db.Cards.ToList());
        }

        // GET: PhoneCards/Details/5
        public ActionResult Details(int? id)
        {
            if (id == null)
            {
                return new HttpStatusCodeResult(HttpStatusCode.BadRequest);
            }
            PhoneCard phoneCard = db.Cards.Find(id);
            if (phoneCard == null)
            {
                return HttpNotFound();
            }
            return View(phoneCard);
        }

        // GET: PhoneCards/Create
        public ActionResult Create()
        {
            return View();
        }

        // POST: PhoneCards/Create
        // To protect from overposting attacks, please enable the specific properties you want to bind to, for 
        // more details see https://go.microsoft.com/fwlink/?LinkId=317598.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public ActionResult Create([Bind(Include = "ID,FirstName,LastName,BirthDate,Address,PhoneNumber")] PhoneCard phoneCard)
        {
            if (ModelState.IsValid)
            {
                db.Cards.Add(phoneCard);
                db.SaveChanges();
                return RedirectToAction("Index");
            }

            return View(phoneCard);
        }

        // GET: PhoneCards/Edit/5
        public ActionResult Edit(int? id)
        {
            if (id == null)
            {
                return new HttpStatusCodeResult(HttpStatusCode.BadRequest);
            }
            PhoneCard phoneCard = db.Cards.Find(id);
            if (phoneCard == null)
            {
                return HttpNotFound();
            }
            return View(phoneCard);
        }

        // POST: PhoneCards/Edit/5
        // To protect from overposting attacks, please enable the specific properties you want to bind to, for 
        // more details see https://go.microsoft.com/fwlink/?LinkId=317598.
        [HttpPost]
        [ValidateAntiForgeryToken]
        public ActionResult Edit([Bind(Include = "ID,FirstName,LastName,BirthDate,Address,PhoneNumber")] PhoneCard phoneCard)
        {
            if (ModelState.IsValid)
            {
                db.Entry(phoneCard).State = EntityState.Modified;
                db.SaveChanges();
                return RedirectToAction("Index");
            }
            return View(phoneCard);
        }

        // GET: PhoneCards/Delete/5
        public ActionResult Delete(int? id)
        {
            if (id == null)
            {
                return new HttpStatusCodeResult(HttpStatusCode.BadRequest);
            }
            PhoneCard phoneCard = db.Cards.Find(id);
            if (phoneCard == null)
            {
                return HttpNotFound();
            }
            return View(phoneCard);
        }

        // POST: PhoneCards/Delete/5
        [HttpPost, ActionName("Delete")]
        [ValidateAntiForgeryToken]
        public ActionResult DeleteConfirmed(int id)
        {
            PhoneCard phoneCard = db.Cards.Find(id);
            db.Cards.Remove(phoneCard);
            db.SaveChanges();
            return RedirectToAction("Index");
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing)
            {
                db.Dispose();
            }
            base.Dispose(disposing);
        }
    }
}