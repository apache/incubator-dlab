/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package com.epam.dlab.exceptions;

/** The exception thrown by the adapter when the convert errors acquired.
 */
public class ParseException extends GenericException {

	private static final long serialVersionUID = -5780834425131769923L;

	/** Constructs a new exception.
	 * @param message error message.
	 */
	public ParseException(String message) {
		super(message);
	}

	/** Constructs a new exception.
	 * @param cause the cause.
	 */
	public ParseException(Exception cause) {
		super(cause);
	}

	/** Constructs a new exception.
	 * @param message error message.
	 * @param cause the cause.
	 */
	public ParseException(String message, Exception cause) {
		super(message, cause);
	}

}