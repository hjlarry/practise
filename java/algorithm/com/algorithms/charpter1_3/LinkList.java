package com.algorithms.charpter1_3;

import com.princeton.StdOut;

import java.util.Iterator;

public class LinkList<Item> implements Iterable<Item> {
    private Node first;
    private Node last;
    private int N;

    private class Node {
        Item item;
        Node next;
    }

    public Iterator<Item> iterator() {
        return new ListIterator();
    }

    private class ListIterator implements Iterator<Item> {
        private Node current = first;

        public boolean hasNext() {
            return current != null;
        }

        public Item next() {
            Item item = current.item;
            current = current.next;
            return item;
        }
    }

    public boolean isEmpty() {
        return N == 0; // first==null也可以
    }

    public void add(Item item) {
        Node old_last = last;
        last = new Node();
        last.item = item;
        if (isEmpty()) {
            first = last;
        } else {
            old_last.next = last;
        }
        N++;
    }

    // ex1.3.20 删除链表的第K个元素
    private boolean delete(int k) {
        if (k > N || k < 1) {
            return false;
        } else {
            int i = 1;
            Node prev = null;
            Node curr = first;
            while (i < k) {
                prev = curr;
                curr = curr.next;

                i++;
            }
            if (k == 1) {
                first = curr.next;
            } else if (k == N) {
                prev.next = null;
            } else {
                prev.next = curr.next;
            }
            N--;
            return true;
        }
    }

    private static void testDelete() {
        LinkList<String> s = new LinkList<>();
        s.add("as");
        s.add("bp");
        s.add("c9");
        s.add("d9");
        for (String t : s) {
            StdOut.println(t);
        }
        StdOut.println();
        s.delete(4);
        for (String t : s) {
            StdOut.println(t);
        }
    }

    // ex 1.3.21
    private boolean find(Item item) {
        Node curr = first;
        while (curr != null && !curr.item.equals(item)) {
            curr = curr.next;
        }
        return curr != null;

    }
    private static void testFind() {
        LinkList<String> s = new LinkList<>();
        s.add("as");
        s.add("bp");
        s.add("c9");
        s.add("d9");
        StdOut.println(s.find("c9"));
    }

    private boolean removeAfter(Item item){
        Node curr = first;
        while (curr != null && !curr.item.equals(item)) {
            curr = curr.next;
        }
        if (curr != null){
            curr.next = null;
            return true;
        }
        return false;
    }

    private static void testRemoveAfter() {
        LinkList<String> s = new LinkList<>();
        s.add("as");
        s.add("bp");
        s.add("c9");
        s.add("d9");
        for (String t : s) {
            StdOut.println(t);
        }
        StdOut.println();
        s.removeAfter("bp");
        for (String t : s) {
            StdOut.println(t);
        }
    }

    public static void main(String[] args) {
        testDelete();
        testFind();
        testRemoveAfter();
    }
}
