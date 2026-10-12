#!/bin/sh
set -eu

f=/usr/include/qt5/QtCore/qfutureinterface.h
if grep -q 'QFutureInterface<void>(State ' "$f"; then
	sed -i \
		-e 's/QFutureInterface<void>(State /QFutureInterface(State /' \
		-e 's/QFutureInterface<void>(const QFutureInterface<void> &other)/QFutureInterface(const QFutureInterface \&other)/' \
		-e 's/QFutureInterface<void> &operator=(const QFutureInterface<void> &other)/QFutureInterface \&operator=(const QFutureInterface \&other)/' \
		"$f"
fi
